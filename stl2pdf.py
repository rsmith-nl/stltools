#! /usr/bin/env python3
# vim:fileencoding=utf-8
#
# Copyright © 2012-2017 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Last modified: 2017-08-22 17:02:28 +0200
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Program for converting a view of an STL file into a PDF file.

Using the -x, -y and -z options you can rotate the object around these axis.
Subsequent rotations will be applied in the order they are given on the
command line.

Note that the object will be automatically centered and scaled to fit in the
picture.
"""

import argparse
import cairo
import logging
import sys
import numpy as np
from stltools import stl, bbox, utils, vecops, matrix

__version__ = '5.0'


def main(argv):
    """
    Entry point of stl2pdf.

    Arguments:
        argv: Command line arguments (without program name!)
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')")
    parser.add_argument(
        '-c',
        '--canvas',
        dest='canvas_size',
        type=int,
        help="canvas size, defaults to 200 PostScript points",
        default=200)
    parser.add_argument(
        '-f',
        '--foreground',
        dest='fg',
        type=str,
        help="foreground color in 6-digit hexdecimal RGB (default E6E6E6)",
        default='E6E6E6')
    parser.add_argument(
        '-b',
        '--background',
        dest='bg',
        type=str,
        help="background color in 6-digit hexdecimal RGB (default FFFFFF)",
        default='FFFFFF')
    parser.add_argument(
        '-o',
        '--output',
        dest='outfile',
        type=str,
        help="output file name",
        default="")
    parser.add_argument(
        '-x',
        type=float,
        action=utils.RotateAction,
        help="rotation around X axis in degrees")
    parser.add_argument(
        '-y',
        type=float,
        action=utils.RotateAction,
        help="rotation around Y axis in degrees")
    parser.add_argument(
        '-z',
        type=float,
        action=utils.RotateAction,
        help="rotation around X axis in degrees")
    parser.add_argument(
        'file', nargs=1, type=str, help='name of the file to process')
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    args.file = args.file[0]
    args.fg = int(args.fg, 16)
    f_red, f_green, f_blue = utils.num2rgb(args.fg)
    args.bg = int(args.bg, 16)
    b_red, b_green, b_blue = utils.num2rgb(args.bg)
    if 'rotations' not in args:
        logging.info('no rotations specified')
        tr = matrix.I()
    else:
        tl = []
        which = {'x': matrix.rotx, 'y': matrix.roty, 'z': matrix.rotz}
        for axis, rot in args.rotations:
            tl.append(which[axis](rot))
        tr = matrix.concat(*tl)
        logging.info('rotation matrix:\n{}'.format(tr))
    if not args.outfile:
        args.outfile = utils.outname(args.file, '.pdf')
        ofs = "no output filename given, using '{}'"
        logging.info(ofs.format(args.outfile))
    logging.info("reading STL file '{}'".format(args.file))
    try:
        vertices, _ = stl.readstl(args.file)
    except ValueError as e:
        logging.error('{}: {}'.format(args.file, e))
        sys.exit(1)
    logging.info('calculating normal vectors')
    facets = vertices.reshape((-1, 3, 3))
    normals = np.array([vecops.normal(a, b, c) for a, b, c in facets])
    logging.info('applying transformations to world coordinates')
    vertices = vecops.xform(tr, vertices)
    normals = vecops.xform(tr[0:3, 0:3], normals)
    logging.info('making model-view matrix')
    minx, maxx, miny, maxy, _, maxz = bbox.makebb(vertices)
    width = maxx - minx
    height = maxy - miny
    dx = -(minx + maxx) / 2
    dy = -(miny + maxy) / 2
    dz = -maxz
    m = matrix.trans([dx, dy, dz])
    sf = min(args.canvas_size / width, args.canvas_size / height)
    v = matrix.scale(sf, -sf)
    v[0, 3], v[1, 3] = args.canvas_size / 2, args.canvas_size / 2
    mv = matrix.concat(m, v)
    logging.info('transforming to view space')
    vertices = vecops.xform(mv, vertices)
    facets = vertices.reshape((-1, 3, 3))
    # In the ortho projection on the z=0 plane, z+ is _towards_ the viewer
    logging.info('Determining visible facets')
    vf = [(f, n, 0.4 * n[2] + 0.5) for f, n in zip(facets, normals)
          if n[2] > 0]
    vfs = '{:.2f}% of facets is visible'
    logging.info(vfs.format(100 * len(vf) / len(facets)))
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices.
    logging.info('depth-sorting visible facets')

    def fkey(t):
        (a, b, c), _, _ = t
        return max(a[2], b[2], c[2])

    vf.sort(key=fkey)
    logging.info('initializing drawing surface')
    out = cairo.PDFSurface(args.outfile, args.canvas_size, args.canvas_size)
    ctx = cairo.Context(out)
    ctx.set_source_rgb(b_red, b_green, b_blue)
    ctx.rectangle(0, 0, args.canvas_size, args.canvas_size)
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.25)
    logging.info('drawing the triangles')
    for (a, b, c), _, i in vf:
        ctx.new_path()
        ctx.move_to(a[0], a[1])
        ctx.line_to(b[0], b[1])
        ctx.line_to(c[0], c[1])
        ctx.close_path()
        ctx.set_source_rgb(f_red*i, f_green*i, f_blue*i)
        ctx.fill_preserve()
        ctx.stroke()
    # Send output.
    out.show_page()
    out.finish()
    logging.info('done')


if __name__ == '__main__':
    main(sys.argv[1:])

#! /usr/bin/env python3
# vim:fileencoding=utf-8
#
# Copyright © 2012-2017 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Last modified: 2017-08-22 17:38:53 +0200
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
Program for converting a view of an STL file into a PostScript file.

Using the -x, -y and -z options you can rotate the object around these axis.
Subsequent rotations will be applied in the order they are given on the command
line.

Note that the object will be automatically centered and scaled to fit in the
picture.
"""

import argparse
import logging
import sys
import time
import numpy as np
from stltools import stl, bbox, utils, vecops, matrix

__version__ = '5.0'


def main(argv):
    """
    Entry point of stl2ps.

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
        help="background color in 6-digit hexdecimal RGB (default white FFFFFF)",
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
        help="rotation around Z axis in degrees")
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
        args.outfile = utils.outname(args.file, '.eps')
        ofs = "no output filename given, using '{}'"
        logging.info(ofs.format(args.outfile))
    logging.info("reading STL file '{}'".format(args.file))
    try:
        vertices, _ = stl.readstl(args.file)
    except ValueError as e:
        logging.error('{}: {}'.format(args.file, e))
        sys.exit(1)
    origbb = bbox.makebb(vertices)
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
    v = matrix.scale(sf, sf)
    v[0, 3], v[1, 3] = args.canvas_size / 2, args.canvas_size / 2
    mv = matrix.concat(m, v)
    logging.info('transforming to view space')
    vertices = vecops.xform(mv, vertices)
    facets = vertices.reshape((-1, 3, 3))
    # In the ortho projection on the z=0 plane, z+ is _towards_ the viewer
    logging.info('determine visible facets')
    vf = [(f, n, 0.4 * n[2] + 0.5) for f, n in zip(facets, normals)
          if n[2] > 0]
    fvs = '{:.2f}% of facets is visible'
    logging.info(fvs.format(100 * len(vf) / len(facets)))
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices.
    logging.info('depth-sorting visible facets')

    def fkey(t):
        (a, b, c), _, _ = t
        return max(a[2], b[2], c[2])

    vf.sort(key=fkey)
    minx, maxx, miny, maxy, _, maxz = bbox.makebb(vertices)
    logging.info('creating PostScript header')
    s1 = "% The scale factor used is: {:.2f} PostScript points/STL-unit"
    s2 = "% This becomes a picture of {:.0f}×{:.0f} PostScript points;"\
         " {:.0f}×{:.0f} mm."
    cs = "%   {:.2f} ≤ {} ≤ {:.2f}"
    lines = [
        "%!PS-Adobe-3.0 EPSF-3.0", "%%BoundingBox: 0 0 {:.0f} {:.0f}".format(
            maxx, maxy), "%%EndComments",
        "% Generated by stl2ps {}".format(__version__),
        "% on {}.".format(time.asctime()), "% Bounding box (STL units)",
        cs.format(origbb[0], 'x', origbb[1]),
        cs.format(origbb[2], 'y', origbb[3]),
        cs.format(origbb[4], 'z', origbb[5]),
        s1.format(sf),
        s2.format(maxx, maxy, maxx / 72 * 25.4,
                  maxy / 72 * 25.4), "% {} of {} facets are visible.".format(
                      len(vf), len(facets))
    ]
    # PostScript settings and macros.
    lines += [
        "% Settings", ".5 setlinewidth", "1 setlinejoin",
        "% Defining drawing commands", "/c {setrgbcolor} def",
        "/f {moveto} def", "/s {lineto} def",
        "/t {lineto closepath gsave fill grestore stroke} def",
        "% Start drawing"
    ]
    # Draw background.
    if b_red < 1 or b_green < 1 or b_blue < 1:
        lines += [
            '% Fill background',
            '{:4.2f} {:4.2f} {:4.2f} c'.format(b_red, b_green, b_blue),
            '0 0 f',
            '{:.0f} 0 s'.format(maxx),
            '{:.0f} {:.0f} s'.format(maxx, maxy),
            '0 {:.0f} t'.format(maxy)
        ]
    # Draw triangles.
    lines += ['% Rendering triangles']
    s3 = "{:4.2f} {:4.2f} {:4.2f} c {:.3f} {:.3f} f {:.3f} {:.3f} s {:.3f} {:.3f} t"
    logging.info('rendering triangles')
    lines += [
        s3.format(f_red*i, f_green*i, f_blue*i, a[0], a[1], b[0], b[1], c[0], c[1])
        for (a, b, c), z, i in vf
    ]
    lines += ["showpage", '%%EOF']
    outs = '\n'.join(lines)
    try:
        with open(args.outfile, "w+") as outf:
            logging.info('writing output file "{}"'.format(args.outfile))
            outf.write(outs)
            logging.info('done')
    except Exception:
        logging.error('cannot write output file "{}"'.format())


if __name__ == '__main__':
    main(sys.argv[1:])

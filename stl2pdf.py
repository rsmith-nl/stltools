#! /usr/bin/env python
# file: stl2pdf.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2011-10-02T18:07:38+02:00
# Last modified: 2022-12-07T23:14:46+0100
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
from stltools import stl, bbox, utils, vecops, matrix, __version__


def main(argv):
    """
    Entry point of stl2pdf.

    Arguments:
        argv: Command line arguments (without program name!)
    """
    args = setup(argv)
    f_red, f_green, f_blue = utils.num2rgb(args.fg)
    if "rotations" not in args:
        logging.info("no rotations specified")
        tr = matrix.I()
    else:
        tl = []
        which = {"x": matrix.rotx, "y": matrix.roty, "z": matrix.rotz}
        for axis, rot in args.rotations:
            tl.append(which[axis](rot))
        tr = matrix.concat(*tl)
        logging.info(f"rotation matrix:\n{tr}")
    if not args.outfile:
        args.outfile = utils.outname(args.file, ".pdf")
        ofs = f'no output filename given, using "{args.outfile}"'
        logging.info(ofs)
    logging.info(f'reading STL file "{args.file}"')
    try:
        vertices, _ = stl.readstl(args.file, args.encoding)
    except ValueError as e:
        logging.error(f"{args.file}: {e}")
        sys.exit(1)
    indices, uvertices = vecops.indexate(vertices)
    del vertices
    logging.info("calculating normal vectors")
    ifacets = list(utils.chunked(indices, 3))
    normals = [
        vecops.normal(uvertices[a], uvertices[b], uvertices[c]) for a, b, c in ifacets
    ]
    cscale = args.canvas_size / 10
    csys = [(0, 0, 0), (cscale, 0, 0), (0, cscale, 0), (0, 0, cscale)]
    logging.info("applying transformations to world coordinates")
    uvertices = vecops.xform(tr, uvertices)
    normals = vecops.xform(tr, normals)
    csys = vecops.xform(tr, csys)
    logging.info("making model-view matrix")
    minx, maxx, miny, maxy, _, maxz = bbox.makebb(uvertices)
    width = maxx - minx
    height = maxy - miny
    dx = -(minx + maxx) / 2
    dy = -(miny + maxy) / 2
    dz = -maxz
    m = matrix.trans([dx, dy, dz])
    sf = min(args.canvas_size / width, args.canvas_size / height)
    v = matrix.scale(sf, -sf)
    v[0][3], v[1][3] = args.canvas_size / 2, args.canvas_size / 2
    mv = matrix.concat(m, v)
    logging.info("transforming to view space")
    uvertices = vecops.xform(mv, uvertices)
    csys = vecops.xform(mv, csys)

    # In the ortho projection on the z=0 plane, z+ is _towards_ the viewer
    logging.info("Determining visible facets")
    vf = [(f, n, 0.4 * n[2] + 0.5) for f, n in zip(ifacets, normals) if n[2] > 0]
    vfs = "{:.2f}% of facets is visible"
    logging.info(vfs.format(100 * len(vf) / len(ifacets)))
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices.
    logging.info("depth-sorting visible facets")

    def fkey(t):
        (a, b, c), _, _ = t
        return max(uvertices[a][2], uvertices[b][2], uvertices[c][2])

    vf.sort(key=fkey)
    logging.info("initializing drawing surface")
    out = cairo.PDFSurface(args.outfile, args.canvas_size, args.canvas_size)
    ctx = cairo.Context(out)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.25)
    logging.info("drawing the triangles")
    for (a, b, c), _, i in vf:
        ctx.new_path()
        ctx.move_to(uvertices[a][0], uvertices[a][1])
        ctx.line_to(uvertices[b][0], uvertices[b][1])
        ctx.line_to(uvertices[c][0], uvertices[c][1])
        ctx.close_path()
        ctx.set_source_rgb(f_red * i, f_green * i, f_blue * i)
        ctx.fill_preserve()
        ctx.stroke()
    logging.info("drawing the axes")
    ctx.new_path()
    ctx.move_to(csys[0][0], csys[0][1])
    ctx.line_to(csys[1][0], csys[1][1])
    ctx.set_source_rgb(1, 0, 0)
    ctx.stroke()
    ctx.new_path()
    ctx.move_to(csys[0][0], csys[0][1])
    ctx.line_to(csys[2][0], csys[2][1])
    ctx.set_source_rgb(0, 1, 0)
    ctx.stroke()
    ctx.new_path()
    ctx.move_to(csys[0][0], csys[0][1])
    ctx.line_to(csys[3][0], csys[3][1])
    ctx.set_source_rgb(0, 0, 1)
    ctx.stroke()
    logging.info("sending output")
    out.show_page()
    out.finish()
    logging.info("done")


def setup(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument(
        "-a",
        "--axes",
        action="store_true",
        help="Add coordinate system in left bottom of image",
    )
    parser.add_argument(
        "-c",
        "--canvas",
        dest="canvas_size",
        type=int,
        help="canvas size, defaults to 200 PostScript points",
        default=200,
    )
    parser.add_argument(
        "-f",
        "--foreground",
        dest="fg",
        type=str,
        help="foreground color in 6-digit hexdecimal RGB (default E6E6E6)",
        default="E6E6E6",
    )
#    parser.add_argument(
#        "-b",
#        "--background",
#        dest="bg",
#        type=str,
#        help="background color in 6-digit hexdecimal RGB (default FFFFFF)",
#        default="FFFFFF",
#    )
    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        help="encoding for the name of the STL object (default utf-8)",
        default="utf-8",
    )
    parser.add_argument(
        "-o", "--output", dest="outfile", type=str, help="output file name", default=""
    )
    parser.add_argument(
        "-x",
        type=float,
        action=utils.RotateAction,
        help="rotation around X axis in degrees",
    )
    parser.add_argument(
        "-y",
        type=float,
        action=utils.RotateAction,
        help="rotation around Y axis in degrees",
    )
    parser.add_argument(
        "-z",
        type=float,
        action=utils.RotateAction,
        help="rotation around X axis in degrees",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("file", nargs=1, type=str, help="name of the file to process")
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    args.file = args.file[0]
    args.fg = int(args.fg, 16)
    return args


if __name__ == "__main__":
    main(sys.argv[1:])

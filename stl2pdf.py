#! /usr/bin/env python2
# vim:fileencoding=utf-8
#
# Copyright © 2012-2014 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
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

'''Program for converting a view of an STL file into a PDF file.'''

from __future__ import print_function, division
import sys
import cairo
import numpy as np
from stltools import stl, bbox, utils, vecops, matrix

__version__ = '$Revision$'[11:-2]


def usage():
    print("""Usage: stl2pdf infile [--output outfile] 
            [--bg background color] [--fg object color]
            [transform [transform ...]]""")
    print("where [transform] is [x number|y number|z number]")
    print("--bg and --fg both take six digit hex color codes of the form xxxxxx.  Please note the lack of '#'")


def main(args):
    """Main program.

    Keyword arguments:
    argv -- command line arguments (without program name!)
    """
    msg = utils.Msg()
    canvas_size = 200
    infile, outfile, tr, bg_color, fg_color = utils.processargs(args, '.pdf', usage)
    if bg_color == None:
        b_red = 1
        b_green = 1
        b_blue = 1
    else:
        b_red, b_green, b_blue = utils.hex2rgb(bg_color)
    if fg_color == None:
        f_red = 0.9
        f_green = 0.9
        f_blue = 0.9
    else:
        f_red, f_green, f_blue = utils.hex2rgb(fg_color)
    msg.say('Reading STL file')
    try:
        vertices, _ = stl.readstl(infile)
    except ValueError as e:
        print((infile + ':', e))
        sys.exit(1)
    msg.say('Calculating normal vectors')
    facets = vertices.reshape((-1, 3, 3))
    normals = np.array([vecops.normal(a, b, c) for a, b, c in facets])
    msg.say('Apply transformations to world coordinates')
    vertices = vecops.xform(tr, vertices)
    normals = vecops.xform(tr[0:3, 0:3], normals)
    msg.say('Making model-view matrix')
    minx, maxx, miny, maxy, _, maxz = bbox.makebb(vertices)
    width = maxx - minx
    height = maxy - miny
    dx = -(minx + maxx)/2
    dy = -(miny + maxy)/2
    dz = -maxz
    m = matrix.trans([dx, dy, dz])
    sf = min(canvas_size/width, canvas_size/height)
    v = matrix.scale(sf, -sf)
    v[0, 3], v[1, 3] = canvas_size/2, canvas_size/2
    mv = matrix.concat(m, v)
    msg.say('Transforming to view space')
    vertices = vecops.xform(mv, vertices)
    facets = vertices.reshape((-1, 3, 3))
    # In the ortho projection on the z=0 plane, z+ is _towards_ the viewer
    msg.say('Determine visible facets')
    vf = [(f, n, 0.4*n[2]+0.5) for f, n in zip(facets, normals) if n[2] > 0]
    msg.say('{:.2f}% of facets is visible'.format(100*len(vf)/len(facets)))
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices.
    msg.say('Depth-sorting visible facets')

    def fkey(t):
        (a, b, c), _, _ = t
        return max(a[2], b[2], c[2])

    vf.sort(None, fkey)
    msg.say('Initialize drawing surface')
    out = cairo.PDFSurface(outfile, canvas_size, canvas_size)
    ctx = cairo.Context(out)
    ctx.set_source_rgb(b_red, b_green, b_blue)
    ctx.rectangle(0,0,canvas_size,canvas_size)
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.25)
    msg.say('Drawing the triangles')
    for (a, b, c), _, i in vf:
        ctx.new_path()
        ctx.move_to(a[0], a[1])
        ctx.line_to(b[0], b[1])
        ctx.line_to(c[0], c[1])
        ctx.close_path()
        ctx.set_source_rgb(f_red, f_green, f_blue)
        ctx.fill_preserve()
        ctx.stroke()
    # Send output.
    out.show_page()
    out.finish()
    msg.say('Done')

if __name__ == '__main__':
    main(sys.argv[1:])

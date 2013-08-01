#! /usr/bin/env python
# -*- python coding: utf-8 -*-
# Copyright © 2012,2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

import sys
import cairo
import numpy as np
from brep import stl, bbox, utils, vecops, matrix


ver = ('stl2pdf [ver. ' + '$Revision$'[11:-2] + 
       '] ('+'$Date$'[7:17]+')')


def usage():
    print ver
    print "Usage: stl2pdf infile [outfile] [transform [transform ...]]"
    print "where [transform] is [x number|y number|z number]"


def main(args):
    """Main program.

    Keyword arguments:
    argv -- command line arguments (without program name!)
    """
    infile, outfile, tr = utils.processargs(args, '.pdf', usage)
    try:
        vertices, _ = stl.readstl(infile)
    except ValueError as e:
        print infile + ':', e
        sys.exit(1)
    # Calculate normals
    facets = vertices.reshape((-1, 3, 3))
    normals = np.array([vecops.normal(a, b, c) for a, b, c in facets])
    # Apply transformations to world coordinates
    vertices = vecops.xform(tr, vertices)
    normals = vecops.xform(tr[0:3, 0:3], normals) 
    # Calculate viewport and projection
    minx, maxx, miny, maxy, _, _ = bbox.makebb(vertices)
    #pr = matrix.ortho(minx, maxx, miny, maxy, minz, maxz)
    width = maxx - minx
    height = maxy - miny
    dx = -width/2
    dy = -height/2
    mv = matrix.trans([dx, dy, 0])
    pr = matrix.I()
    pr[2, 2] = 0
    # still to do, determine the scaling factor.
    mvp = matrix.concat(pr, mv)
    vertices = vecops.xform(mvp, vertices)
    facets = vertices.reshape((-1, 3, 3))
    # In the ortho projection on the z=0 plane, z+ is _towards_ the viewer
    vf = [(f, n, -0.4*n[2]+0.5) for f, n in zip(facets, normals) if n[2] > 0]
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices.
    def fkey(t):
        (a, b, c), _, _ = t
        return max(a[2], b[2], c[2])
    vf.sort(None, fkey)
    # Initialize drawing surface
    out = cairo.PDFSurface(outfile, 200, 200)
    ctx = cairo.Context(out)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.25)
    # Draw the triangles. The transform is needed because Cairo uses a
    # different coordinate system.
    ctx.transform(cairo.Matrix(1.0, 0.0, 0.0, -1.0, 200, 0))
    for (a, b, c), _, i in vf:
        ctx.new_path()
        ctx.move_to(a[0], a[1])
        ctx.line_to(b[0], b[1])
        ctx.line_to(c[0], c[1])
        ctx.close_path()
        ctx.set_source_rgb(i, i, i)
        ctx.fill_preserve()
        ctx.stroke()
    # Send output.
    out.show_page()
    out.finish()

if __name__ == '__main__':
    main(sys.argv[1:])

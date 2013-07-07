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
from brep import stl, xform, bbox, utils


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
        ifacets, points, _ = stl.readstl(infile)
        inormals, vectors = stl.normals(ifacets, points)
    except ValueError as e:
        print infile + ':', e
        sys.exit(1)
    # Apply transformations
    points  = [tr.applyto(p) for p in points]
    vectors  = [tr.applyrot(v) for v in vectors]
    # Calculate viewport and transformation
    minx, maxx, miny, maxy, _, _ = bbox.makebb(points)
    pr = xform.Zpar(minx, maxx, miny, maxy)
    out = cairo.PDFSurface(outfile, pr.w, pr.h)
    ctx = cairo.Context(out)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.25)
    # Calculate the visible facets
    vf = [(f, n) for f, n in zip(ifacets, inormals) 
          if pr.isvisible(vectors[n])]
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices.
    def fkey(t):
        (a, b, c), _ = t
        return max(points[a][2], points[b][2], points[c][2])
    vf.sort(None, fkey)
    ppoints = [pr.applyto(p) for p in points]
    intensity = [0.4*v[2]+0.5 for v in vectors]
    # Draw the triangles. The transform is needed because Cairo uses a
    # different coordinate system.
    ctx.transform(cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, pr.h))
    for (a, b, c), ni in vf:
        ctx.new_path()
        ctx.move_to(ppoints[a][0], ppoints[a][1])
        ctx.line_to(ppoints[b][0], ppoints[b][1])
        ctx.line_to(ppoints[c][0], ppoints[c][1])
        ctx.close_path()
        ctx.set_source_rgb(intensity[ni], intensity[ni], intensity[ni])
        ctx.fill_preserve()
        ctx.stroke()
    # Send output.
    out.show_page()
    out.finish()

if __name__ == '__main__':
    main(sys.argv[1:])

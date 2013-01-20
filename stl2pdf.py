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
import os
import cairo
from brep import stl, xform


name = ('stl2pdf [ver. ' + '$Revision$'[11:-2] + 
       '] ('+'$Date$'[7:-2]+')')


def usage():
    print name
    print "Usage: stl2pdf infile [outfile] [transform [transform ...]]"
    print "where [transform] is [x number|y number|z number]"


def getargs(args):
    """ Process the command-line arguments.

    Returns:
    A tuple containing the input file name, the output filename and
    the transformation matrix.
    """
    validargs = ['x', 'y', 'z', 'X', 'Y', 'Z']
    if len(args) < 1:
        usage()
        sys.exit(0)
    infile = args[0]
    if len(args) < 2 or args[1] in validargs:
        outfile = None
        del args[:1]
        outbase = os.path.basename(infile)
        if outbase.endswith((".stl", ".STL")):
            outbase = outbase[:-4]
        outfile = outbase+".pdf"
    else:
        outfile = args[1]
        del args[:2]
    tr = xform.Xform()
    while len(args) > 1:
        if not args[0] in validargs:
            print "Unknown argument '{}' ignored.".format(args[0])
            del args[0]
            continue
        try:
            ang = float(args[1])
            if args[0] in ['x','X']:
                tr.rotx(ang)
            elif args[0] in ['y','Y']:
                tr.roty(ang)
            else:
                tr.rotz(ang)
            del args[:2]
        except:
            print "Argument '{}' is not a number, ignored.".format(args[1])
            continue
    return (infile, outfile, tr)

def main(args):
    """Main program.

    Keyword arguments:
    argv -- command line arguments (without program name!)
    """
    infile, outfile, tr = getargs(args)
    try:
        stlobj = stl.fromfile(infile)
    except:
        print "The file '{}' cannot be read or parsed. Exiting.".format(infile)
        sys.exit(1)
    # Apply transformations
    stlobj.xform(tr)
    # Calculate viewport and transformation
    xmin, xmax, ymin, ymax, zmin, zmax = stlobj.extents() #pylint: disable=W0612
    pr = xform.Zpar(xmin, xmax, ymin, ymax)
    out = cairo.PDFSurface(outfile, pr.w, pr.h)
    ctx = cairo.Context(out)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(0.25)
    # Calculate the visible facets
    pf = [f for f in stlobj.projected_facets(pr)]
    # Next, depth-sort the facets using the largest z-value of the
    # three vertices. 
    pf.sort(None, lambda f: max([f[3][0], f[3][1], f[3][2]]))
    # Draw the triangles. The transform is needed because Cairo uses a
    # different coordinate system.
    ctx.transform(cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, pr.h))
    for f in pf:
        ctx.new_path()
        ctx.move_to(f[0][0], f[0][1])
        ctx.line_to(f[1][0], f[1][1])
        ctx.line_to(f[2][0], f[2][1])
        ctx.close_path()
        ctx.set_source_rgb(f[4], f[4], f[4])
        ctx.fill_preserve()
        ctx.stroke()
    # Send output.
    out.show_page()
    out.finish()

if __name__ == '__main__':
    main(sys.argv[1:])

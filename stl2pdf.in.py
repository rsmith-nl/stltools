#! /usr/bin/env python
# -*- python coding: utf-8 -*-
# Program for converting a view of an STL file into a PDF file
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-12-20 18:52:09 rsmith>
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

import sys
import math
import os

import stl
import xform

from reportlab.pdfgen import canvas

name = "stl2pdf [rev. VERSION] (DATE)"

def usage():
    print name
    print "Usage: stl2pdf infile [outfile] [transform [transform ...]]"
    print "where [transform] is [x number|y number|z number]"

## This is the main program ##
# Process the command-line arguments
validargs = ['x', 'y', 'z', 'X', 'Y', 'Z']
if len(sys.argv) == 1:
    usage()
    sys.exit(0)
infile = sys.argv[1]
if len(sys.argv) < 3 or sys.argv[2] in validargs:
    outfile = None
    del sys.argv[:2]
else:
    outfile = sys.argv[2]
    del sys.argv[:3]
tr = xform.Xform()
while len(sys.argv) > 1:
    if not sys.argv[0] in validargs:
        print "Unknown argument '{}' ignored.".format(sys.argv[0])
        del sys.argv[0]
        continue
    try:
        ang = float(sys.argv[1])
        if sys.argv[0] in ['x','X']:
            tr.rotx(ang)
        elif sys.argv[0] in ['y','Y']:
            tr.roty(ang)
        else:
            tr.rotz(ang)
        del sys.argv[:2]
    except:
        print "Argument '{}' is not a number, ignored.".format(sys.argv[1])
        continue
# Open the file
stlobj = stl.Object(infile)
# Remove spaces from name
stlobj.name = stlobj.name.strip()
# Apply transformations
if tr.unity == False:
    stlobj.xform(tr)
# Calculate viewport and transformation
xmin, xmax, ymin, ymax, zmin, zmax = stlobj.extents()
pr = xform.Zpar(xmin, xmax, ymin, ymax)
# Prepare output.
if outfile == None:
    outbase = os.path.basename(infile)
    if outbase.endswith((".stl", ".STL")):
        outbase = outbase[:-4]
    outfile = outbase+".pdf"
out = canvas.Canvas(outfile, (pr.w, pr.h), pageCompression=1)
out.setCreator(name)
out.setLineCap(1)
out.setLineJoin(2)
out.setLineWidth(0.25)
# Calculate the visible facets
vizfacets = [f for f in stlobj.facet if pr.visible(f.n)]
# Next, depth-sort the facets using the largest z-value of the three vertices.
vizfacets.sort(None, lambda f: max([f.v[0].z, f.v[1].z, f.v[2].z]))
# Project and illuminate the facets
pf = [stl.ProjectedFacet(f, pr) for f in vizfacets]
# Draw the triangles
for f in pf:
    path = out.beginPath()
    path.moveTo(f.x1, f.y1)
    path.lineTo(f.x2, f.y2)
    path.lineTo(f.x3, f.y3)
    path.close()
    out.setFillGray(f.gray)
    out.setStrokeGray(f.gray)
    out.drawPath(path, 1, 1)
# Send output.
out.showPage()
try:
    out.save()
except:
    print "Cannot write output file '{}'.".format(outfile)
    sys.exit(2)

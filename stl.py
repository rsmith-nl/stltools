#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Classes for handling STL files and trianglulated models.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-04-09 13:30:43 rsmith>
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

import math
import struct
import string

limit = 1e-7

class Vertex:
    '''Class for a 3D point in Cartesian space.'''
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    def __add__(self, other):
        return Vertex(self.x + other.x, self.y + other.y, self.z + other.z)
    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)
    def __eq__(self, other):
        if (math.fabs(self.x - other.x) < limit and 
            math.fabs(self.y - other.y) < limit and 
            math.fabs(self.z - other.z) < limit):
            return True
        else:
            return False

class Normal(Vertex):
    '''Class for a 3D normal vector in Cartesian space.'''
    def __init__(self, dx, dy, dz):
        dx = float(dx)
        if math.fabs(dx) < limit: dx = 0.0
        dy = float(dy)
        if math.fabs(dy) < limit: dy = 0.0
        dz = float(dz)
        if math.fabs(dz) < limit: dz = 0.0
        l = math.sqrt(dx*dx+dy*dy+dz*dz)
        if l == 0.0:
            raise ValueError
        Vertex.__init__(self, dx/l, dy/l, dz/l)

class Facet:
    '''Class for a 3D triangle.'''
    def __init__(self, p1, p2, p3, n):
        '''Initialize the Facet from the Vertices and a Normal.'''
        self.v = [p1, p2, p3]
        self.n = n
    def __str__(self):
        s = "[facet normal {} {} {}\n".format(self.n.x, self.n.y, self.n.z)
        s += "   outer loop\n"
        for t in range(3):
            s += "     vertex {} {} {}\n".format(self.v[t].x, self.v[t].y, 
                                                 self.v[t].z)
        s += "   endloop\n"
        s += " endfacet]"
        return s

class File:
    '''Class for reading STL files.'''
    def __init__(self, fname):
        '''Open the STL file fname.'''
        f = open(fname)
        contents = f.read()
        f.close()
        self.facet = []
        if contents.find("solid") == -1:
            # Binary format.
            self.name,nf1 = struct.unpack("=80sI",contents[0:84])
            # Strip zero bytes and whitespace on both sides.
            self.name = self.name.strip(string.whitespace+chr(0))
            contents = contents[84:]
            facetsz = len(contents)
            nf2 = facetsz/50
            if nf1 != nf2:
                ds = "stl.File; from '{}': {} facets, from size {} facets"
                print ds.format(self.name, nf1, nf2)
                raise ValueError
            # Chop the string into a list of 50 byte strings.
            items = [contents[n:n+50] for n in range(0,facetsz,50)]
            # Process the items
            for i in items:
                nx, ny, nz, f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
                    struct.unpack("=ffffffffffffxx", i)
                norm = Normal(nx, ny, nz)
                v1 = Vertex(f1x,f1y,f1z)
                v2 = Vertex(f2x,f2y,f2z)
                v3 = Vertex(f3x,f3y,f3z)
                f =  Facet(v1, v2, v3, norm)
                self.facet.append(f)
        else:
            # Text format.
            items = contents.split()
            items = [s.strip() for s in items]
            sn = items.index("solid")+1
            en = items.index("facet")
            self.name = ' '.join(items[sn:en])
            nf2 = items.count("endfacet")
            del items[0:en]
            # Items now begins with "facet"
            while items[0] == "facet":
                norm = Normal(items[2], items[3], items[4])
                v1 = Vertex(items[8], items[9], items[10])
                v2 = Vertex(items[12], items[13], items[14])
                v3 = Vertex(items[16], items[17], items[18])
                f =  Facet(v1, v2, v3, norm)
                self.facet.append(f)
                del items[:21]
        if nf2 != len(self.facet):
            raise ValueError
    def __len__(self): return len(self.facet)
    def __iter__(self):
        for f in self.facet:
            yield f
    def __str__(self):
        return "[stl.File; name: '{}', {} facets]".format(self.name, 
                                                          len(self.facet))
    def extents(self):
        '''Returns the maximum and minimum x, y and z coordinates'''
        f = self.facet[0]
        xmin = f.v[0].x
        ymin = f.v[0].y
        zmin = f.v[0].z
        xmax = f.v[0].x
        ymax = f.v[0].y
        zmax = f.v[0].z
        for k in range(3):
            for f in self.facet:
                if f.v[k].x < xmin: xmin = f.v[k].x
                elif f.v[k].x > xmax: xmax = f.v[k].x
                if f.v[k].y < ymin: ymin = f.v[k].x
                elif f.v[k].y > ymax: ymax = f.v[k].y
                if f.v[k].z < zmin: zmin = f.v[k].z
                elif f.v[k].z > zmax: zmax = f.v[k].z
        if -limit < xmin <limit: xmin = 0.0
        if -limit < xmax <limit: xmax = 0.0
        if -limit < ymin <limit: ymin = 0.0
        if -limit < ymax <limit: ymax = 0.0
        if -limit < zmin <limit: zmin = 0.0
        if -limit < zmax <limit: zmax = 0.0
        return (xmin,xmax,ymin,ymax,zmin,zmax)

# Built-in test.
if __name__ == '__main__':
    print "===== begin of binary file ====="
    fname = "test/salamanders.stl"
    binstl = File(fname)
#    for n,f in enumerate(binstl):
#        print n, f
    print binstl
    print "[bin] len(binstl) = {}".format(len(binstl))
    print "[bin] extents = ", binstl.extents()
    print "[bin] 0", binstl.facet[0]
    print "..."
    print "[bin] {}".format(len(binstl)-1), binstl.facet[-1]
    print "===== end of binary file ====="
    print "===== begin of text file ====="
    fname = "test/microSD_connector.stl"
    txtstl = File(fname)
#    for n,f in enumerate(txtstl):
#        print n, f
    print txtstl
    print "len(txtstl) = {}".format(len(txtstl))
    print "[txt] extents = ", txtstl.extents()
    print "[txt] 0", txtstl.facet[0]
    print "..."
    print "[txt] {}".format(len(txtstl)-1), txtstl.facet[-1]
    print "===== end of text file ====="

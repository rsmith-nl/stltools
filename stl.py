#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Classes for handling STL files and trianglulated models.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-04-04 22:44:07 rsmith>
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

class Vertex:
    '''Class for a 3D point.'''
    err = 1e-7
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    def __add__(self, other):
        return Vertex(self.x + other.x, self.y + other.y, self.z + other.z)
    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)
    def __eq__(self, other):
        if (math.fabs(self.x - other.x) < err and 
            math.fabs(self.y - other.y) < err and 
            math.fabs(self.z - other.z) < err):
            return True
        else:
            return False

class Normal(Vertex):
    '''Class for a 3D normal vector.'''
    def __init__(self, dx, dy, dz):
        dx = float(dx)
        dy = float(dy)
        dz = float(dz)
        l = math.sqrt(dx*dx+dy*dy+dz*dz)
        if l == 0.0:
            raise ValueError
        Vertex.__init__(self, dx/l, dy/l, dz/l)

class Facet:
    '''Class for a 3D triangle.'''
    def __init__(self, p1, p2, p3, n):
        '''Initialize the Facet from the Vertices and a Normal.'''
        self.v = []
        self.v.append(p1)
        self.v.append(p2)
        self.v.append(p3)
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
    def _readbinary(self):
        if len(self.iterf) == 0:
            return None
        nx, ny, nz, f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
            struct.unpack("=ffffffffffffxx", self.iterf[0])
        del self.iterf[0]
        norm = Normal(nx, ny, nz)
        v1 = Vertex(f1x,f1y,f1z)
        v2 = Vertex(f2x,f2y,f2z)
        v3 = Vertex(f3x,f3y,f3z)
        return Facet(v1, v2, v3, norm)
    def _readtext(self):
        try:
            n = self.iterf.index("facet")+1
        except:
            return None
        del self.iterf[0:n]
        norm = Normal(self.iterf[1], self.iterf[2], self.iterf[3])
        v1 = Vertex(self.iterf[7], self.iterf[8], self.iterf[9])
        v2 = Vertex(self.iterf[11], self.iterf[12], self.iterf[13])
        v3 = Vertex(self.iterf[15], self.iterf[16], self.iterf[17])
        del self.iterf[:17]
        return Facet(v1, v2, v3, norm)
    def __init__(self, filename):
        f = open(filename)
        contents = f.read()
        f.close()
        if contents.find("solid") == -1:
            # Binary format.
            self.readfunc = self._readbinary
            self.name,self.nf = struct.unpack("=80sI",contents[0:84])
            contents = contents[84:]
            facetsz = len(contents)
            nf = facetsz/50
            if self.nf != nf:
                ds = "stl.File; from '{}': {} facets, from size {} facets"
                print ds.format(self.name, self.nf, nf)
            # Chop the string into a list of 50 byte strings.
            self.items = [contents[n:n+50] for n in range(0,facetsz,50)]
            self.iterf = self.items[:]
        else:
            # Text format.
            self.readfunc = self._readtext
            self.items = contents.split()
            self.items = [s.strip() for s in self.items]
            sn = self.items.index("solid")+1
            en = self.items.index("facet")
            self.name = ' '.join(self.items[sn:en])
            self.nf = self.items.count("endfacet")
            self.iterf = self.items[:]
    def __len__(self): return self.nf
    def __iter__(self): return self
    def __next__(self):
        facet = self.readfunc()
        if facet == None:
            self.iterf = self.items[:]
            raise StopIteration
        return facet
    def next(self):
        return self.__next__()

# Built-in test.
if __name__ == '__main__':
    print "===== begin of binary file ====="
    binfile = File("test/salamanders.stl")
    for f in binfile:
        print f
    print "===== end of binary file ====="
    print "===== begin of text file ====="
    txtfile = File("test/microSD_connector.stl")
    for f in txtfile:
        print f
    print "===== end of text file ====="

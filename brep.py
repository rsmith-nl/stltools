# -*- coding: utf-8 -*-
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

# Check this code with 'pylint -r n brep.py'

'''Classes for handling triangulated models.'''

__version__ = '$Revision$'[11:-2]

import struct
import numpy as np

class TriSurf(object):

    def __init__(self, fn=None):
        self.fn = fn
        self.name = None
        self.v = np.array([], dtype=float) # vertices
        self.tv = None # transformed vertices
        self.pv = np.array([], dtype=float) # projected vertices
        self.n = np.array([], dtype=float) # normals
        self.tn = None # transformed normals
        self.e = [] # edges
        self.f = [] # facets
        if fn == None:
            self.reader = None
            return
        with open(self.fn) as stlf:
            data = stlf.read()
        if data.find('vertex', 80) == -1:
            self.reader = self._readbinary(data)
        else:
            self.reader = self._readtext(data)

    def addfacet(self, a, b, c):
        '''Create a facet from the three points a, b and c.

        Arguments:
        a -- numpy array containing the coordinates of the first vertex.
        b -- numpy array containing the coordinates of the second vertex.
        c -- numpy array containing the coordinates of the third vertex.
        '''
        # Calculate normal vector.
        u = b-a
        v = c-b
        n = np.cross(u, v)
        if np.all(n == 0):
            raise ValueError
        n /= (n*n).sum()**0.5
        # Add normal vector to list.
        newnormal = 1
        if len(self.n) == 0:
            self.n = np.array([n])
            ni = 0
        else:
            where = np.ravel(np.nonzero(np.all(n == self.n, axis=1)))
            if len(where) == 0:
                ni = len(self.n)
                self.n = np.vstack((self.n, n))
            else:
                ni = where[0]
                newnormal = 0
        # Add vertices to list if not already in it.
        vi = []
        newverts = 3
        for t in a, b, c:
            if len(self.v) == 0:
                self.v = np.array([t])
                vi.append(0)
            else:
                where = np.ravel(np.nonzero(np.all(t == self.v, axis=1)))
                if len(where) == 0:
                    vi.append(len(self.v))
                    self.v = np.vstack((self.v, t))
                else:
                    vi.append(where[0])
                    newverts -= 1
        # Calculate the edges, store them in an edge list.
        edges = [tuple(sorted(vi[0:2])), tuple(sorted(vi[1:3])), 
                    (vi[0], vi[2])]
        # Add new triangle to the list.
        self.f.append([vi, ni, edges, False, 0.0])
        # Return the number of new vertices and normals
        return newverts, newnormal
        
    def _readbinary(self, contents=None):
        '''Process the contents of a binary STL file as a
        generator.

        Arguments:
        contents -- file data.
        '''
        self.name, nf1 = struct.unpack("=80sI", contents[0:84])
        # Strip zero bytes, the prefix 'solid' and whitespace.
        self.name = self.name.replace("solid ", "")
        self.name = self.name.strip('\x00 \t\n\r')
        if len(self.name) == 0:
            self.name = "unknown"
        contents = contents[84:]
        facetsz = len(contents)
        nf2 = facetsz / 50
        if nf1 != nf2:
            raise ValueError("Number of facets doesn't match file size.")
        # Chop the string into a list of 50 byte strings.
        items = [contents[n:n+50] for n in range(0, facetsz, 50)]
        del contents
        # Process the items
        et = 'skipped degenerate facet {}.'
        for i in items:
            f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
            struct.unpack("=12x9f2x", i)
            v1 = np.array([f1x, f1y, f1z], dtype=float)
            v2 = np.array([f2x, f2y, f2z], dtype=float)
            v3 = np.array([f3x, f3y, f3z], dtype=float)
            try:
                nv, nn = self.addfacet(v1, v2, v3)
            except ValueError:
                yield et.format(len(self.f))
            ot = 'facet {}/{}: {} new vertices, {} new normals.'
            yield ot.format(len(self.f), nf1, nv, nn)

    def _readtext(self, contents=None):
        '''Process the contents of a text STL file as a
        generator.
        '''
        items = contents.split()
        del contents
        items = [s.strip() for s in items]
        try:
            sn = items.index("solid")+1
            en = items.index("facet")
        except:
            raise ValueError("Not an STL file.")
        if sn == en:
            self.name = "unknown"
        else:
            self.name = ' '.join(items[sn:en])
        nf1 = items.count('facet')
        del items[0:en]
        # Items now begins with "facet"
        et = 'skipped degenerate facet {}.'
        while items[0] == "facet":
            v1 = np.array([items[8], items[9], items[10]], dtype=float)
            v2 = np.array([items[12], items[13], items[14]], dtype=float)
            v3 = np.array([items[16], items[17], items[18]], dtype=float)
            try:
                nv, nn = self.addfacet(v1, v2, v3)
            except ValueError:
                yield et.format(len(self.f))
            del items[:21]
            ot = 'facet {}/{}: {} new vertices, {} new normals.'
            yield ot.format(len(self.f), nf1, nv, nn)

    def zproj(self):
        '''Perform a Z parallel projection.
        '''
        if self.tv == None:
            self.tv = self.v.copy()
        sizes = (self.tv.max(0) - self.tv.min(0))[:2]

    def move(self, v):
        '''Perform a translation.

        Arguments:
        v -- translation vector
        '''        
        self.tv = self.v + v

    def rotate(self, v, a):
        '''Perform a rotation.
        '''        
        pass



# Built-in test.
if __name__ == '__main__':
    print "===== begin of text file ====="
    fname = "test/cube.stl"
    txtstl = TriSurf(fname)
    for r in txtstl.reader:
        print r
    print 'vertices:', txtstl.v
    print 'normals:', txtstl.n
    print 'facets:', txtstl.f
    print "===== end of text file ====="
    print "===== begin of binary file ====="
    fname = "test/ad5-rtm-light.stl"
    binstl = TriSurf(fname)
    for r in binstl.reader:
        print r
    print 'vertices:', binstl.v
    print 'normals:', binstl.n
    print 'facets:', binstl.f
    print "===== end of binary file ====="

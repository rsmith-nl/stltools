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


def fromstl(fname):
    t = TriSurf2(fname)
    for f in t.reader:
        pass
    return t

class TriSurf(object):

    def __init__(self, fn=None):
        self.fn = fn
        self.name = None
        self.v = [] # vertices
        self.sv = set()
        self.tv = [] # transformed vertices
        self.pv = [] # projected vertices
        self.n = [] # normals
        self.sn = set()
        self.tn = [] # transformed normals
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
        a -- tuple containing the coordinates of the first vertex.
        b -- tuple containing the coordinates of the second vertex.
        c -- tuple containing the coordinates of the third vertex.
        '''
        # Calculate normal vector.
        u = _sub(b, a)
        v = _sub(c, b)
        n = _cross(u, v)
        n  = _norm(n)
        # Add normal vector to list.
        if n in self.sn:
            ni = self.n.index(n)
            newnormal = 0
        else:
            ni = len(self.n)
            self.n.append(n)
            self.sn.add(n)
            newnormal = 1
        # Add vertices to list if not already in it.
        vi = []
        newverts = 3
        for t in a, b, c:
            if t in set(self.sv):
                vi.append(self.v.index(t))
                newverts -= 1
            else:
                vi.append(len(self.v))
                self.v.append(t)
                self.sv.add(t)
        # Calculate the edges, store them in an edge list.
        edges = [tuple(sorted(vi[0:2])), tuple(sorted(vi[1:3])), 
                    (vi[0], vi[2])]
        # Add new triangle to the list.
        self.f.append([vi, ni, edges, False, 0.0])
        # Return the number of new vertices and normals
        return newverts, newnormal

    def getbb(self):
        '''Calculate the bounding box.
        '''
        x = [p[0] for p in self.v]
        y = [p[1] for p in self.v]
        z = [p[2] for p in self.v]
        return ((min(x), max(x)), (min(y), max(y)), (min(z), max(z)))
        
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
            v1 = (f1x, f1y, f1z)
            v2 = (f2x, f2y, f2z)
            v3 = (f3x, f3y, f3z)
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
            v1 = (float(items[8]), float(items[9]), float(items[10]))
            v2 = (float(items[12]), float(items[13]), float(items[14]))
            v3 = (float(items[16]), float(items[17]), float(items[18]))
            try:
                nv, nn = self.addfacet(v1, v2, v3)
            except ValueError:
                yield et.format(len(self.f))
            del items[:21]
            ot = 'facet {}/{}: {} new vertices, {} new normals.'
            yield ot.format(len(self.f), nf1, nv, nn)

    def __len__(self):
        '''The length of a TriSurf is defined as the number of facets.
        '''
        return len(self.f)

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


def _add(a, b):
    '''Calculate and return a+b.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    '''
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def _sub(a, b):
    '''Calculate and return a-b.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    '''
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def _cross(a, b):
    '''Calculate and return the cross product of a and b.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    '''
    return (a[1]*b[2] - a[2]*b[1], 
            a[2]*b[0] - a[0]*b[2], 
            a[0]*b[1] - a[1]*b[0])

def _norm(a):
    '''Calculate and return the normalized a.
    
    Arguments
    a -- 3-tuple of floats
    '''
    L = (a[0]**2 + a[1]**2 + a[2]**2)**0.5
    if L == 0.0:
        raise ValueError('zero-length normal vector')
    return (a[0]/L, a[1]/L, a[2]/L)


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

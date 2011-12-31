# -*- coding: utf-8 -*-
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-12-31 02:50:24 rsmith>
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

#Check this code with 'pylint -r n stl.py'

"Classes for handling STL files and trianglulated models."

import hashlib
import math
import struct

# Points less than 'LIMIT' apart are considered equal.
LIMIT = 1e-7

class Vertex(object):
    '''Class for a 3D point in Cartesian space.'''

    def __init__(self, x, y, z):
        '''Creates a Vertex from the given x,y and z coordinates.'''
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        ks = '({},{},{})'.format(self.x, self.y, self.z)
        self._key =  hashlib.md5(ks).hexdigest() # pylint: disable=E1101

    def __add__(self, other):
        '''Return the sum of 'self' and 'other' as a new vertex.'''
        return Vertex(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        '''Return the difference of 'self' and 'other' as a new vertex.'''
        return Vertex(self.x - other.x, self.y - other.y, self.z - other.z)

    def __str__(self):
        vs = '      vertex {} {} {}'
        return vs.format(self.x, self.y, self.z)

    def __eq__(self, other):
        if other == None:
            return False
        if (math.fabs(self.x - other.x) < LIMIT and 
            math.fabs(self.y - other.y) < LIMIT and 
            math.fabs(self.z - other.z) < LIMIT):
            return True
        else:
            return False

    def __len__(self):
        '''Distance of a Vertex to the origin.'''
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

    def xform(self, tr):
        '''Apply the transformation tr to the vertex.'''
        (self.x, self.y, self.z) = tr.apply(self.x, self.y, self.z)
        ks = '({},{},{})'.format(self.x, self.y, self.z)
        self._key =  hashlib.md5(ks).hexdigest() # pylint: disable=E1101

    def cross(self, b):
        '''Returns the cross product of self and b.'''
        return Vertex(self.y*b.z-self.z*b.y, 
                      self.z*b.x-self.x*b.z, 
                      self.x*b.y-self.y*b.x)

    def key(self):
        '''Returns a unique key for the vertex so we can put it in a
        dictionary.'''
        return self._key

class Normal(Vertex):
    '''Class for a 3D normal vector in Cartesian space.'''

    def __init__(self, dx, dy, dz):
        '''Set the normal from normalized values of dx, dy and dz.
           This will raise a ValueError if the length of the vector is 0.'''
        dx = float(dx)
        dy = float(dy)
        dz = float(dz)
        l = math.sqrt(dx*dx+dy*dy+dz*dz)
        if l == 0.0:
            raise ValueError("Length of vector is 0!")
        Vertex.__init__(self, dx/l, dy/l, dz/l)

    def set(self, dx, dy, dz):
        self.__init__(dx, dy, dz)

    def __str__(self):
        ns = '  facet normal {} {} {}'
        return ns.format(self.x, self.y, self.z)

    def xform(self, tr):
        '''Apply the transformation (without the translation part) tr to the
        normal.'''
        (self.x, self.y, self.z) = tr.applyrot(self.x, self.y, self.z)


class Edge(object):
    '''Class representing the edge of a Facet, a line segment between two
    vertices.'''

    def __init__(self, start, end, f=None):
        '''Create the edge of a Facet.
        
        start, end -- points of the line segment
        f   -- facet that the line segment belongs to.'''
        assert isinstance(start, Vertex), "Start point of edge is not a Vertex"
        assert isinstance(end, Vertex), "End point of edge is not a Vertex"
        self.p = [start, end]
        self.refs = []
        if f:
            assert isinstance(f, Facet), "Reference is not a Facet."
            self.refs.append(f)

    def __eq__(self, other):
        '''If both self and other contain the same endpoints, they're equal,
        irrespective of the direction of the edge.'''
        assert isinstance(Edge, other), "Trying to compare a non-Edge."
        if self.p[0] == other.p[0] and self.p[1] == other.p[1]:
            return True
        if self.p[0] == other.p[1] and self.p[1] == other.p[0]:
            return True
        return False

    def __str__(self):
        s = 'Edge from ({}, {}, {}) to ({}, {}, {}) ({} refs)'
        return s.format(self.p[0].x, self.p[0].y, self.p[0].z, 
                        self.p[1].x, self.p[1].y, self.p[1].z,
                        len(self.refs))

    def fits(self, index, other):
        '''Checks if another Edge fits onto this one.

        index -- end of the Edge to test, either 1 (start) or 2 (end).
        other -- Edge to test.

        Returns a tuple of the new end edge and its free point.'''
        index = int(index)
        assert index < 0 or index > 2, "Index out of bounds"
        assert isinstance(Edge, other), "Trying to fit a non-Edge."
        if self.p[index-1] == other.p[0]:
            return (other, 1)
        if self.p[index-1] == other.p[1]:
            return (other, 2)
        return (self, index) # Doesn't fit

    def addref(self, f):
        '''Add another Facet to the list of references.'''
        assert isinstance(f, Facet), "Reference is not a Facet."
        self.refs.append(f)

    def key(self):
        '''Return a unique key for the edge so we can put it in a
        dictionary. The key is derived from the keys of the Edge's
        Vertices.'''
        k1 = self.p[0].key()
        k2 = self.p[1].key()
        if k2 < k1:
            return k2+k1
        return k1+k2

class Facet(object):
    '''Class for a 3D triangle.'''

    def __init__(self, p1, p2, p3, n):
        '''Initialize the Facet from the Vertices p1, p2 and p3 
        and a Normal n.'''
        assert isinstance(p1, Vertex)
        assert isinstance(p2, Vertex)
        assert isinstance(p3, Vertex)
        self.v = [p1, p2, p3]
        if isinstance(n, Normal):
            self.n = n
        else:
            d1 = p2 - p1
            d2 = p3 - p2
            xp = d1.cross(d2)
            self.n = Normal(xp.x, xp.y, xp.z)

    def __str__(self):
        s = str(self.n)+'\n'
        s += '    outer loop\n'
        s += str(self.v[0])+'\n'
        s += str(self.v[1])+'\n'
        s += str(self.v[2])+'\n'
        s += '    endloop\n  endfacet'
        return s

class ProjectedFacet(object):
    '''Class for a 3D triangle projected on 2 2D surface.'''
    def __init__(self, f, pr):
        '''Initialize the ProjectedFacet from the Facet f, and a Zpar pr.'''
        ambient = 0.05
        delta = 0.8
        (self.x1, self.y1) = pr.project(f.v[0].x, f.v[0].y, f.v[0].z)
        (self.x2, self.y2) = pr.project(f.v[1].x, f.v[1].y, f.v[1].z)
        (self.x3, self.y3) = pr.project(f.v[2].x, f.v[2].y, f.v[2].z)
        self.gray = f.n.z*delta+ambient
        if self.gray < ambient:
            self.gray = ambient
        elif self.gray > (ambient+delta):
            self.gray = ambient+delta
        # Bounding box
        self.xmin = min(self.x1, self.x2, self.x3)
        self.ymin = min(self.y1, self.y2, self.y3)
        self.xmax = max(self.x1, self.x2, self.x3)
        self.ymax = max(self.y1, self.y2, self.y3)


class Surface(object):
    '''Class for STL objects.'''

    def __init__(self, fn=None):
        '''Read the STL file fn into an STL surface. Create an empty STL
        object if fn is None.'''
        self.facets = []
        self.vertices = {}
        self.normals = {}
        self.name = ""
        self.xmin = self.xmax = None
        self.ymin = self.ymax = None
        self.zmin = self.zmax = None
        self.mx = self.my = self.mz = 0.0
        if fn == None:
            return
        f = open(fn)
        con = f.read()
        f.close()
        if con.find("vertex", 80) == -1:
            self._process_bin(con)
        else:
            self._process_txt(con)

    def __str__(self):
        s = "solid {}\n".format(self.name)
        for f in self.facets:
            s += str(f)+'\n'
        s += 'endsolid'
        return s

    def _process_bin(self, contents):
        '''Process the contents of a binary file.'''
        self.name, nf1 = struct.unpack("=80sI", contents[0:84])
        # Strip zero bytes, the prefix 'solid' and whitespace on both sides.
        self.name = self.name.replace("solid ", "")
        self.name = self.name.strip('\x00 \t\n\r')
        if len(self.name) == 0:
            self.name = "unknown"
        contents = contents[84:]
        facetsz = len(contents)
        nf2 = facetsz/50
        if nf1 != nf2:
            raise ValueError("Number of facets doesn't match file size.")
        # Chop the string into a list of 50 byte strings.
        items = [contents[n:n+50] for n in range(0, facetsz, 50)]
        # Process the items
        for i in items:
            nx, ny, nz, f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
                struct.unpack("=ffffffffffffxx", i)
            v1 = Vertex(f1x, f1y, f1z)
            v2 = Vertex(f2x, f2y, f2z)
            v3 = Vertex(f3x, f3y, f3z)
            try:
                norm = Normal(nx, ny, nz)
            except ValueError:
                norm = None
            self.addfacet(v1, v2, v3, norm)

    def _process_txt(self, contents):
        '''Process the contents of a text file.'''
        items = contents.split()
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
        del items[0:en]
        # Items now begins with "facet"
        while items[0] == "facet":
            v1 = Vertex(items[8], items[9], items[10])
            v2 = Vertex(items[12], items[13], items[14])
            v3 = Vertex(items[16], items[17], items[18])
            try:
                norm = Normal(items[2], items[3], items[4])
            except ValueError:
                norm = None
            self.addfacet(v1, v2, v3, norm)
            del items[:21]

    def addfacet(self, v1, v2, v3, norm):
        '''Make vertices v1, v2, v3 and optionally normal vector norm into a
        Facet and add it to the STL object.'''
        k1 = v1.key()
        if k1 not in self.vertices:
            self.vertices[k1] = v1
        k2 = v2.key()
        if k2 not in self.vertices:
            self.vertices[k2] = v2
        k3 = v3.key()
        if k3 not in self.vertices:
            self.vertices[k3] = v3
        f =  Facet(self.vertices[k1], self.vertices[k2], 
                   self.vertices[k3], norm)
        if not isinstance(norm, Normal):
            norm = f.n
        kn = norm.key()
        if kn not in self.normals:
            self.normals[kn] = norm
        else:
            # Make sure the facet references the normal in the dict!
            f.n = self.normals[kn]
        self.facets.append(f)
        self._updateextents(f)

    def __len__(self): 
        return len(self.facets)

    def __iter__(self):
        for f in self.facets:
            yield f

    def extents(self):
        '''Returns the maximum and minimum x, y and z coordinates in the 
           form of a tuple (xmin, xmax, ymin, ymax, zmin, zmax).'''
        return (self.xmin, self.xmax, self.ymin, self.ymax, 
                self.zmin, self.zmax)

    def center(self):
        '''Returns the midpoint of the extents in a tuple (x, y, z).'''
        return ((self.xmin+self.xmax)/2, (self.ymin+self.ymax)/2, 
                (self.zmin+self.zmax)/2)

    def meanpoint(self):
        '''Returns the average of all Vertexes of all Facets 
           in a tuple (x, y, z).'''
        c = 3*len(self.facets)
        return (self.mx/c, self.my/c, self.mz/c)

    def stats(self, prefix=''):
        '''Returns a string with various information about the object.'''
        outs = prefix + "Name of the solid: '{}'.\n".format(self.name)
        s = prefix 
        s += "{} facets, {} unique vertices, {} unique normal vectors.\n"
        outs += s.format(len(self.facets), len(self.vertices), 
                         len(self.normals))
        outs += prefix + "3D Extents of the model (in STL units):\n"
        outs += prefix + "{} ≤ x ≤ {},\n".format(self.xmin, self.xmax)
        outs += prefix + "{} ≤ y ≤ {},\n".format(self.ymin, self.ymax)
        outs += prefix + "{} ≤ z ≤ {}.\n".format(self.zmin, self.zmax)
        s = "3D center (midpoint of extents, STL units): <{0}, {1}, {2}>.\n"
        x, y, z = self.center()
        outs += prefix + s.format(x, y, z)
        s = "3D mean (mean of all vertices, STL units): <{0}, {1}, {2}>."
        x, y, z = self.meanpoint()
        outs += prefix + s.format(x, y, z)
        return outs

    def _updateextents(self, f):
        '''Update the extents for Facet f.'''
        if self.xmin == None:
            self.xmin = self.xmax = f.v[0].x
            self.ymin = self.ymax = f.v[0].y
            self.zmin = self.zmax = f.v[0].z
            self.mx = 0.0
            self.my = 0.0
            self.mz = 0.0
        self.mx += f.v[0].x + f.v[1].x + f.v[2].x
        self.my += f.v[0].y + f.v[1].y + f.v[2].y
        self.mz += f.v[0].z + f.v[1].z + f.v[2].z
        for k in range(3):
            if f.v[k].x < self.xmin: 
                self.xmin = f.v[k].x
            elif f.v[k].x > self.xmax: 
                self.xmax = f.v[k].x
            if f.v[k].y < self.ymin: 
                self.ymin = f.v[k].y
            elif f.v[k].y > self.ymax: 
                self.ymax = f.v[k].y
            if f.v[k].z < self.zmin: 
                self.zmin = f.v[k].z
            elif f.v[k].z > self.zmax: 
                self.zmax = f.v[k].z

    def xform(self, tr):
        '''Transform all points and normals.'''
        vd = {}
        for v in self.vertices.itervalues():
            v.xform(tr)
            k = v.key()
            vd[k] = v
        del self.vertices
        self.vertices = vd
        nd = {}
        for n in self.normals.itervalues():
            n.xform(tr)
            k = n.key()
            nd[k] = n
        del self.normals
        self.normals = nd
        self.xmin = None
        for f in self.facets:
            self._updateextents(f)

    def edges(self):
        '''Returns a list of all edges in the Surface.'''
        de = {}
        for f in self.facets:
            for j in range(0, 3):
                k = j +1
                if k > 2:
                    k = 0
                ne = Edge(f.v[j], f.v[k], f)
                s = ne.key()
                if s in de:
                    de[s].addref(f)
                else:
                    de[s] = ne
        return de.values()

# Built-in test.
if __name__ == '__main__':
    print "===== begin of binary file ====="
    fname = "test/salamanders.stl"
    binstl = Surface(fname)
    print binstl.stats("[bin] ")
    print "[bin] 0", binstl.facets[0]
    print "..."
    print "[bin] {}".format(len(binstl)-1), binstl.facets[-1]
    print "===== end of binary file ====="
    print "===== begin of text file ====="
    fname = "test/microSD_connector.stl"
    txtstl = Surface(fname)
    print txtstl.stats('[txt] ')
    print "[txt] 0", txtstl.facets[0]
    print "..."
    print "[txt] {}".format(len(txtstl)-1), txtstl.facets[-1]
    print "===== end of text file ====="
    cube = Surface('test/cube.stl')
    print cube.stats('[cube] ')
    el = cube.edges()
    print '[cube] {} unique edges'.format(len(el))
    for e in el:
        print '[cube]', e

# -*- coding: utf-8 -*-
# Copyright © 2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
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

# Check this code with 'pylint -r n stl.py'

"""Reading triangulated models."""

__version__ = '$Revision$'[11:-2]

import struct
from os.path import basename
from collections import namedtuple
from .vector import *

Facet = namedtuple('Facet', ['a', 'b', 'c', 'n', 'l'])

class FacetMesh(object): # pylint: disable=R0924
    """The Facets class is designed to hold raw data read from an STL
    file. Instances are generally created by the fromfile() function
    """

    def __init__(self, name):
        """Creates an empty FacetMesh instance.

        Arguments:
        name -- string containing the name of the object
        """
        self.name = name.strip()
        self.facets = []
        self.degenerate_facets = []

    def length(self): 
        return len(self.facets)

    def bbox(self):
        """Calculate the bounding box of a FacetMesh.

        Returns:
        A vector.BoundingBox containing the minimal and maximal value
        in x, y and z direction of all points.
        """
        if not self.facets:
            raise ValueError('empty Facet list')
        points  = [p for fct in self.facets for p in (fct.a, fct.b, fct.c)]
        return vector.BoundingBox(points)

    def addfacet(self, f):
        """Add a facet to the FacetMesh object. Mainly for use in the
        fromfile() function. 

        Arguments:
        f -- a 3-tuple of Vectors
        """
        a, b, c = f
        n = vector.normal(a, b, c)
        if n:
            self.facets.append(Facet(a, b, c, n, None))
        else:
            self.degenerate_facets.append(f)

    def stats(self, prefix=''):
        """Produces a string containing statistics about the object.
        """
        bb = self.bbox() 
        outs = prefix + 'Model name: "{}"\n'.format(self.name)
        outs += prefix + '{} facets\n'.format(len(self.facets))
        dft = '{} degenerate facets\n'
        outs += prefix + dft.format(len(self.degenerate_facets))
        outs += prefix + "3D Extents of the model (in STL units):\n"
        outs += prefix + "{} ≤ x ≤ {},\n".format(bb.minx, bb.maxx)
        outs += prefix + "{} ≤ y ≤ {},\n".format(bb.miny, bb.maxy)
        outs += prefix + "{} ≤ z ≤ {}.\n".format(bb.minz, bb.maxz)
        s = "3D center (midpoint of extents, STL units): <{0}, {1}, {2}>.\n"
        outs += prefix + s.format((bb.minx + bb.maxx)/2.0, 
                                  (bb.miny + bb.maxy)/2.0, 
                                  (bb.minz + bb.maxz)/2.0)
        s = "3D mean (mean of all vertices, STL units): <{0}, {1}, {2}>."
        points = [f.a for f in self.facets]
        points += [f.b for f in self.facets]
        points += [f.c for f in self.facets]
        x, y, z = vector.mean(points)
        outs += prefix + s.format(x, y, z)
        return outs

    def xform(self, t):
        """Apply the transformation t to the object.

        Arguments:
        t -- Xform object.
        """
        #TODO: should this return a copy?
        self.facets = [Facet(t.apply(f.a), t.apply(f.b), t.apply(f.c),
                             t.applyrot(f.n)) for f in self.facets]

    def projected_facets(self, pr):
        """Generates visible projected facets

        Arguments:
        pr -- Zpar object.

        Yields:
        a tuple containing three 2-tuples with the projected vertices,
        a 3-tuple of the z-values of the vertices for depth sorting
        and the z-value of the normal vector.
        """        
        for f in self.facets:
            if pr.isvisible(f.n):
                yield (pr.point(f.a), pr.point(f.b), pr.point(f.c),
                       (f.a.z, f.b.z, f.c.z), f.n.z)


class IndexedMesh(object): # pylint: disable=R0924
    """The IndexedMesh uses indices into a list if unique points and
    normals to describe facets. Thus the facets remain the same even
    is the list of points and normals are transformed or projected.
    """

    def __init__(self, a):
        """Create an empty IndexedMesh.

        Arguments:
        a -- a string containing the name of the object, or a Facets
        instance.
        """
        if isinstance(a, str):
            self.name = a
            self.points = []
            self.normals = []
            self.ilines = []
            self.ifacets = []
            self.bb = None
        elif isinstance(a, FacetMesh):
            c = make_indexed_mesh(a)
            self.name = c.name
            self.points = c.points
            self.normals = c.normals
            self.ifacets = c.ilines
            self.ifacets = c.ifacets
            self.bb = c.bb
        else:
            raise ValueError('a must be a string or a FacetMesh instance')

    def __str__(self):
        outs = "solid {}\n".format(self.name)
        for (v, n, l) in self.ifacets: # pylint: disable=W0612
            nv = self.normals[n]
            outs +=  '  facet normal {} {} {}\n'.format(nv.x, nv.y, nv.z)
            outs += '    outer loop\n'
            for i in v:
                p = self.points[i]
                outs += '      vertex {} {} {}\n'.format(p.x, p.y, p.z)
            outs += '    endloop\n  endfacet\n'
        outs += 'endsolid\n'
        return outs

    def length(self):
        return len(self.ifacets)

    def xform(self, t):
        """Apply the transformation t to the object.

        Arguments:
        t -- Xform object.
        """
        #TODO: should this return a copy?
        self.points = [t.apply(p)  for p in self.points]
        self.normals = [t.applyrot(n)  for n in self.normals]

    def addfacet(self, f):
        """Add a facet to the IndexedMesh object. Mainly for creating
        an IndexedMesh by hand. The make_indexed_mesh() function
        should be used to convert a Facets object into an IndexedMesh.

        Arguments:
        f -- a tuple of Vectors (a,b,c,n) or (a,b,c)
        """
        if len(f) == 4:
            a, b, c, n = f
        elif len(f) == 3:
            a, b, c = f
            n = vector.normal(a, b, c)
        else:
            raise ValueError('facet must be a 3-tuple or 4-tuple')
        if n == None:
            return 'Skipped degenerate facet.'
        stat = ''
        # Normal vector
        ni = vector.lstindex(self.normals, n)
        if ni == len(self.normals) - 1:
            stat += 'Found 1 new normal, index {}. '.format(ni)
        # Vertices:
        pi = vector.lstindex(self.points, [a,b,c])
        nnp = [i for i in pi if i>ol]
        if nnp:
            stat += 'Found {} new points; {}. '.format(len(nnp), str(nnp))
        # Lines
        nl = [sorted(i) for i in [(pi[0], pi[1]), (pi[1], pi[2]), 
                                  (pi[2], [pi[0]])]]
        li = []
        for l in nl:
            try:
                li.append(self.ilines.index(l))
            except ValueError:
                li.append(len(self.ilines))
                self.ilines.append(l)
        # Facet
        nf = Facet(pi[0], pi[1], pi[2], ni, li)
        self.ifacets.append(nf)
        return stat

    def stats(self, prefix=''):
        """Return statistics about an STL model.
        """
        self.update_extents()
        s = prefix + 'Model name: "{}"\n'.format(self.name)
        s = prefix + "{} facets, {} vertices, {} normal vectors.\n"
        outs = s.format(len(self.ifacets), len(self.points), 
                        len(self.normals))
        outs += prefix + "3D Extents of the model (in STL units):\n"
        outs += prefix + "{} ≤ x ≤ {},\n".format(self.xmin, self.xmax)
        outs += prefix + "{} ≤ y ≤ {},\n".format(self.ymin, self.ymax)
        outs += prefix + "{} ≤ z ≤ {}.\n".format(self.zmin, self.zmax)
        s = "3D center (midpoint of extents, STL units): <{0}, {1}, {2}>.\n"
        outs += prefix + s.format((self.xmin + self.xmax)/2.0, 
                                  (self.ymin + self.ymax)/2.0, 
                                  (self.zmin + self.zmax)/2.0)
        s = "3D mean (mean of all vertices, STL units): <{0}, {1}, {2}>."
        x, y, z = vector.mean(self.points)
        outs += prefix + s.format(x, y, z)
        return outs

    def update_extents(self):
        x = [p.x for p in self.points]
        y = [p.y for p in self.points]
        z = [p.z for p in self.points]
        self.bb = vector.BoundingBox(min(x), max(x), min(y), max(y),
                                     min(z), max(z))

    def projected_facets(self, pr):
        """Generates visible projected facets

        Arguments:
        pr -- Zpar object.

        Yields: 
        a tuple containing three 2-tuples with the projected vertices,
        a 3-tuple of the z-values of the vertices for depth sorting
        and the z-value of the normal vector.
        """        
        pp = [pr.point(i) for i in self.points]
        pn = [pr.isvisible(i) for i in self.normals]
        for pi, ni, li in self.ifacets: #pylint: disable=W0612
            if pn[ni]:
                ix, iy, iz = pi
                yield (pp[ix], pp[iy], pp[iz], 
                       (self.points[ix][2], self.points[iy][2], 
                        self.points[iz][2]), self.normals[ni])


def fromfile(fname):
    """Read an STL file.
    
    Arguments:
    fname -- filename to read the STL file from.

    Returns:
    a Facets object.
    """
    def _readbinary(items=None):
        """Process the contents of a binary STL file as a
        generator.

        Arguments:
        items -- file data minus header split into 50-byte blocks.

        Yields:
        a 3-tuple of Vectors
        """
        # Process the items
        for i in items:
            f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
            struct.unpack("=12x9f2x", i)
            a = vector.Vector(f1x, f1y, f1z)
            b = vector.Vector(f2x, f2y, f2z)
            c = vector.Vector(f3x, f3y, f3z)
            yield (a, b, c)

    def _readtext(items=None):
        """Process the contents of a text STL file as a
        generator.

        Arguments:
        items -- stripped lines of the text STL file

        Yields:
        a nested tuple ((x1,y1,z1),(x2,y2,z2),(x3,y3,z3))
        """
        # Items now begins with "facet"
        while items[0] == "facet":
            a = vector.Vector(float(items[8]), float(items[9]),
                              float(items[10])) 
            b = vector.Vector(float(items[12]), float(items[13]),
                              float(items[14]))
            c = vector.Vector(float(items[16]), float(items[17]),
                              float(items[18]))
            del items[:21]
            yield (a, b, c)

    with open(fname, 'r') as stlfile:
        data = stlfile.read()
    if data.find('vertex', 120) == -1: # Binary file format
        name, nf1 = struct.unpack("=80sI", data[0:84])
        name = name.replace("solid ", "")
        name = name.strip('\x00 \t\n\r')
        if len(name) == 0:
            name = basename(fname)[:-4]
        data = data[84:]
        facetsz = len(data)
        nf2 = facetsz / 50
        if nf1 != nf2:
            raise ValueError("Number of facets doesn't match file size.")
        items = [data[n:n+50] for n in range(0, facetsz, 50)]
        reader = _readbinary(items)
    else: # Text file format
        items = [s.strip() for s in data.split()]
        try:
            sn = items.index("solid")+1
            en = items.index("facet")
        except:
            raise ValueError("Not an STL file.")
        if sn == en:
            name = 'unknown'
        else:
            name = ' '.join(items[sn:en])
        nf1 = items.count('facet')
        del items[0:en]
        reader = _readtext(items)
    fl = FacetMesh(name)
    for f in reader:
        fl.addfacet(f)
    return fl


def make_indexed_mesh(f):
    """Creates an IndexedMesh instance from a Facets instance.

    Arguments:
    f -- Facets instance

    Returns:
    an IndexedMesh instance.
    """
    def _process_points(facets):
        """Find all unique points in the facets.

        Arguments:
        facets -- a list of Facets

        Returns:
        A tuple (upoints, ifacets) where
        upoints -- a list of unique points
        ifacets -- a list of facets 
        """
        points = [p for fct in facets for p in (fct.a, fct.b, fct.c)]
        indexes = todo = range(len(points))
#        todo = range(len(points))
        for j in todo:
            # with every list comprehension, m becomes smaller so
            # don't try and fit it in a single one. It will most
            # probably be slower.
            m = [i for i in xrange(j+1, len(points)) if points[i][0] ==
                 points[j][0]]
            m = [i for i in m if points[i][1] == points[j][1]]
            m = [i for i in m if points[i][2] == points[j][2]]
            # m is now a list of all indexes of points equal to points[j]
            for i in m:
                indexes[i] = j
                todo.remove(i)
        u = sorted(list(set(indexes)))
        upoints = [points[i] for i in u]
        x = {u[i]: i for i in xrange(len(u))}
        ni = [x[i] for i in indexes]
        ifacets = [(ni[i], ni[i+1], ni[i+2]) for i in xrange(0, len(ni), 3)]
        return upoints, ifacets
    def _process_normals(facets):
        """Find all unique normal vectors in the facets.

        Arguments:
        facets -- a list of 4-tuples (a,b,c,n) where the first three are
        3-tuples containing vertex coordinates and the last is is a
        3-tuple containing a normalized normal vector.

        Returns:
        A tuple (unormals, ni) where
        unormals -- a list of unique 3-tuples each containing a normal
        vector.
        ifacets -- a list of facet normals which are indexes into the
        unormals list.
        """
        normals = [f[3] for f in facets]
        indexes = range(len(normals))
        todo = range(len(normals))
        for j in todo:
            m = [i for i in xrange(j+1, len(normals)) if normals[i][0] ==
                 normals[j][0]]
            m = [i for i in m if normals[i][1] == normals[j][1]]
            m = [i for i in m if normals[i][2] == normals[j][2]]
            # m is now a list of all indexes of normal equal to normals[j]
            for i in m:
                indexes[i] = j
                todo.remove(i)
        u = sorted(list(set(indexes)))
        unormals = [normals[i] for i in u]
        x = {u[i]: i for i in xrange(len(u))}
        ni = [x[i] for i in indexes]
        return unormals, ni
    upoints, fi = _process_points(f.facets)
    unormals, ni = _process_normals(f.facets)
    s = IndexedMesh(f.name)
    s.points = upoints
    s.update_extents()
    s.normals = unormals
    li = [((c[0], c[1]),(c[1], c[2]),(c[2], c[0])) for c in fi]
    s.ifacets = zip(fi, ni, li)
    return s

def box(name, dx=1.0, dy=1.0, dz=1.0):
    """Creates a box-shaped IndexedMesh object of dimensions dx, dy,
    dz centered on (0,0,0)"""
    b = IndexedMesh(name)
    dx = float(dx)/2.0
    dy = float(dy)/2.0
    dz = float(dz)/2.0
    p = [(-dx, -dy,  dz), ( dx, -dy,  dz), ( dx, -dy, -dz),
         (-dx, -dy, -dz), (-dx,  dy,  dz), ( dx,  dy,  dz),
         ( dx,  dy, -dz), (-dx,  dy, -dz)]
    b.addfacet((p[0], p[1], p[4]))
    b.addfacet((p[1], p[5], p[4]))
    b.addfacet((p[0], p[2], p[1]))
    b.addfacet((p[0], p[3], p[2]))
    b.addfacet((p[4], p[5], p[6]))
    b.addfacet((p[4], p[6], p[7]))
    b.addfacet((p[3], p[7], p[2]))
    b.addfacet((p[7], p[6], p[2]))
    b.addfacet((p[1], p[2], p[5]))
    b.addfacet((p[5], p[2], p[6]))
    b.addfacet((p[0], p[4], p[3]))
    b.addfacet((p[3], p[4], p[7]))
    b.update_extents()
    return b

def cylinder(name, r, h, n=32):
    """Creates a cylindrical IndexedMesh object with radius r, height
    h and each circle divided into n segments. """
    pass


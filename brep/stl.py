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

# Check this code with 'pylint -r n read.py'

"""Reading triangulated models."""

__version__ = '$Revision$'[11:-2]

import struct
from os.path import basename
from . import vector

class Facets(object): # pylint: disable=R0924
    """The Facets class is designed to hold raw data read from an STL
    file. Instances are generally created by the fromfile() function
    """

    def __init__(self, name):
        """Creates an empty Facets instance.

        Arguments:
        name -- string containing the name of the object
        """
        self.name = name.strip()
        self.facets = []
        self.degenerate_facets = []

    def __len__(self): 
        return len(self.facets)

    def extents(self):
        """Calculate the extents of a Facet.

        Returns:
        a 6-tuple containing the minimal and maximal value in x, y and
        z direction of all points.
        """
        if not self.facets:
            raise ValueError('empty Facets object')
        points  = [p for fct in self.facets for p in fct[0:3]]
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        z = [p[2] for p in points]
        return (min(x), max(x), min(y), max(y), min(z), max(z))

    def addfacet(self, f):
        """Add a facet to the Facets object. Mainly for use in the
        fromfile() function. A facet is a 4-tuple (a,b,c,n) where a, b
        and c are vertices and n is the normalized normal vector.

        Arguments:
        f -- a nested tuple ((x1,y1,z1),(x2,y2,z2),(x3,y3,z3))
        """
        a, b, c = f
        u = vector.sub(b, a)
        v = vector.sub(c, b)
        n = vector.cross(u, v) # Calculate the normal vector
        try:
            n  = vector.norm(n)
            self.facets.append((a, b, c, n))
        except ValueError:
            self.degenerate_facets.append(f)

    def stats(self, prefix=''):
        """Produces a string containing statistics about the object.
        """
        minx, maxx, miny, maxy, minz, maxz = self.extents() 
        outs = prefix + 'Model name: "{}"\n'.format(self.name)
        outs += prefix + '{} facets\n'.format(len(self.facets))
        dft = '{} degenerate facets\n'
        outs += prefix + dft.format(len(self.degenerate_facets))
        outs += prefix + "3D Extents of the model (in STL units):\n"
        outs += prefix + "{} ≤ x ≤ {},\n".format(minx, maxx)
        outs += prefix + "{} ≤ y ≤ {},\n".format(miny, maxy)
        outs += prefix + "{} ≤ z ≤ {}.\n".format(minz, maxz)
        s = "3D center (midpoint of extents, STL units): <{0}, {1}, {2}>.\n"
        outs += prefix + s.format((minx + maxx)/2.0, 
                                  (miny + maxy)/2.0, 
                                  (minz + maxz)/2.0)
        s = "3D mean (mean of all vertices, STL units): <{0}, {1}, {2}>."
        points = [f[0] for f in self.facets]
        points += [f[1] for f in self.facets]
        points += [f[2] for f in self.facets]
        x, y, z = vector.mean(points)
        outs += prefix + s.format(x, y, z)
        return outs

    def xform(self, t):
        """Apply the transformation t to the object.

        Arguments:
        t -- Xform object.
        """
        self.facets = [(t.apply(f[0]), t.apply(f[1]), t.apply(f[2]),
                        t.applyrot(f[3])) for f in self.facets]

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
            if pr.visible(f[3]):
                yield (pr.point(f[0]), pr.point(f[1]), pr.point(f[2]),
                       (f[0][2], f[1][2], f[2][2]), f[3][2])


class IndexedMesh(object): # pylint: disable=R0924
    """The IndexedMesh uses indices into a list if unique points and
    normals to describe facets. Thus the facets remain the same even
    is the list of points and normals are transformed or projected.
    """

    def __init__(self, name):
        """Create an empty IndexedMesh.

        Arguments:
        name -- string containing the name of the object
        """
        self.name = name
        self.points = []
        self.normals = []
        self.ifacets = []
        self.xmin = self.xmax = None
        self.ymin = self.ymax = None
        self.zmin = self.zmax = None

    def __str__(self):
        outs = "solid {}\n".format(self.name)
        for (v, n, l) in self.ifacets: # pylint: disable=W0612
            nv = self.normals[n]
            outs +=  '  facet normal {} {} {}\n'.format(nv[0], nv[1], nv[2])
            outs += '    outer loop\n'
            for i in v:
                p = self.points[i]
                outs += '      vertex {} {} {}\n'.format(p[0], p[1], p[2])
            outs += '    endloop\n  endfacet\n'
        outs += 'endsolid\n'
        return outs

    def __len__(self):
        return len(self.ifacets)

    def xform(self, t):
        """Apply the transformation t to the object.

        Arguments:
        t -- Xform object.
        """
        self.points = [t.apply(p)  for p in self.points]
        self.normals = [t.applyrot(n)  for n in self.normals]

    def addfacet(self, f):
        """Add a facet to the IndexedMesh object. Mainly for creating
        an IndexedMesh by hand. The make_indexed_mesh() function
        should be used to convert a Facets object into an IndexedMesh.

        Arguments:
        f -- a nested tuple ((x1,y1,z1),(x2,y2,z2),(x3,y3,z3))
        """
        a, b, c, n = f
        if n == None:
            return 'Skipped degenerate facet.'
        stat = ''
        # Normal vector
        try:
            ni = self.normals.index(n)
        except ValueError:
            ni = len(self.normals)
            self.normals.append(f[3])
            stat += 'Found 1 new normal, index {}. '.format(ni)
        # Vertices:
        pi = []
        nnp = []
        for x in a, b, c:
            try:
                pi.append(self.points.index(x))
            except ValueError:
                i = len(self.points)
                pi.append(i)
                self.points.append(x)
                nnp.append(i)
        if nnp:
            stat += 'Found {} new points; {}. '.format(len(nnp), str(nnp))
        # Lines
        li = ((pi[0], pi[1]), (pi[1], pi[2]), 
              (pi[2], pi[0]))
        # Facet
        self.ifacets.append((tuple(pi), ni, li))
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
        x = [p[0] for p in self.points]
        y = [p[1] for p in self.points]
        z = [p[2] for p in self.points]
        self.xmin = min(x)
        self.xmax = max(x)
        self.ymin = min(y)
        self.ymax = max(y)
        self.zmin = min(z)
        self.zmax = max(z)

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
        pn = [pr.visible(i) for i in self.normals]
        for pi, ni, li in self.facets:
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
        a nested tuple ((x1,y1,z1),(x2,y2,z2),(x3,y3,z3))
        """
        # Process the items
        for i in items:
            f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
            struct.unpack("=12x9f2x", i)
            a = (f1x, f1y, f1z)
            b = (f2x, f2y, f2z)
            c = (f3x, f3y, f3z)
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
            a = (float(items[8]), float(items[9]), float(items[10]))
            b = (float(items[12]), float(items[13]), float(items[14]))
            c = (float(items[16]), float(items[17]), float(items[18]))
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
    fl = Facets(name)
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
    upoints, fi = _process_points(f.facets)
    unormals, ni = _process_normals(f.facets)
    s = IndexedMesh(f.name)
    s.points = upoints
    s.update_extents()
    s.normals = unormals
    li = [((c[0], c[1]),(c[1], c[2]),(c[2], c[0])) for c in fi]
    s.ifacets = zip(fi, ni, li)
    return s


def _process_points(facets):
    """Find all unique points in the facets.

    Arguments:
    facets -- a list of 4-tuples (a,b,c,n) where the first three are
    3-tuples containing vertex coordinates and the last is is a
    3-tuple containing a normalized normal vector.

    Returns:
    A tuple (upoints, ifacets) where
    upoints -- a list of unique 3-tuples each containing vertex
    coordinates
    ifacets -- a list of facets as 3-tuples of integers which are
    indexes into the upoints list.
    """
    points = [p for fct in facets for p in fct[0:3]]
    indexes = range(len(points))
    todo = range(len(points))
    for j in todo:
        m = [i for i in xrange(j+1, len(points)) if points[i][0] ==
             points[j][0]]
        m = [i for i in m if points[i][1] == points[j][1]]
        m = [i for i in m if points[i][2] == points[j][2]]
        # m is now a list of all indexes of points equal to points[j]
        for i in m:
            indexes[i] = j
            todo.remove(i)
#        print j, 'is the same point as', m
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
#        print j, 'is the same normal as', m
    u = sorted(list(set(indexes)))
    unormals = [normals[i] for i in u]
    x = {u[i]: i for i in xrange(len(u))}
    ni = [x[i] for i in indexes]
    return unormals, ni

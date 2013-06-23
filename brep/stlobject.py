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

"""STL models."""

from __future__ import print_function
import vecops
import bbox

__version__ = '$Revision$'[11:-2]

class RawStl(object):
    """A data representation of a raw STL file. Contains a combined list of
    facet vertices and normal vectors.
    """

    def __init__(self, name):
        if name == None or len(name) == 0:
            name = 'unknown'
        self.name = name
        # normal vector. 
        self._facets = []

    def __str__(self):
        fs = '''  facet normal {}
    outer loop
      vertex {}
      vertex {}
      vertex {}
    endloop
  endfacet'''
        lines = ['solid {}'.format(self.name)] 
        lines += [fs.format(vecops.mkstr(n), vecops.mkstr(a), vecops.mkstr(b),
                            vecops.mkstr(c)) for a, b, c, n in self._facets]
        lines += ['endsolid']
        return '\n'.join(lines)

    @property
    def facets(self):
        """Return the facets as a tuple. Each facet is a 4-tuple (a, b, c, n) 
        of 3-tuples. The first three are the facet's points, the last is the
        normal vector.
        """
        return tuple(self._facets)

    @property
    def numfacets(self):
        return len(self._facets)

    def addfacet(self, f):
        """Add a single facet to a RawStl.

        Arguments:
        f -- a 3-tuple of 3-tuples

        Exceptions:
        ValueError -- when a degenerate facet is found.
        """
        assert isinstance(f, tuple) and len(f) == 3
        a, b, c, = f
        n = vecops.normal(a, b, c)
        if vecops.length(n) == 0:
            raise ValueError('degenerate facet')
        self._facets.append((a, b, c, n))

    def addfacets(self, lf):
        """Add a list of facets to a RawStl. Degenerate facets (with a
        0-length normal vector) are not added. But their indices in the lf
        array are returned.

        Arguments:
        lf -- a list of 3-tuples of vector.Vector3 objects
        """
        comb = [(a, b, c, vecops.normal(a, b, c)) for a, b, c in lf]
        degenerates = [n for n, c in enumerate(comb) 
                       if vecops.length(c[3]) == 0]
        self._facets += [(a, b, c, vecops.normalize(n)) for a, b, c, n 
                         in comb if vecops.length(n) > 0]
        return degenerates

    def bbox(self):
        """Return the BoundingBox of the object."""
        return bbox.make([p for a, b, c, _ in self._facets for p in a, b, c])

    def xform(self, m):
        """Transforms the raw STL object."""
        newfacets = [((m.applyto(a), m.applyto(b), m.applyto(c)),
                       m.applyrot(n)) for a, b, c, n in self._facets]
        self._facets = newfacets


class IndexedStl(object):
    """In this representation, all the vertices and normal vectors are 
    unique, and the facet list is a list of indices into the vertex and
    normal lists.
    """

    def __init__(self, name=''):
        self.name = name
        self._vertices = []
        self._normals = []
        self._facets = []

    def __str__(self):
        fs = '''  facet normal {}
    outer loop
      vertex {}
      vertex {}
      vertex {}
    endloop
  endfacet'''
        lines = ['solid {}'.format(self.name)] 
        lines += [fs.format(vecops.mkstr(self._normals[n]),
                            vecops.mkstr(self._vertices[a]), 
                            vecops.mkstr(self._vertices[b]),
                            vecops.mkstr(self._vertices[c])) 
                  for a, b, c, n in self._facets]
        lines += ['endsolid']
        return '\n'.join(lines)

    @staticmethod
    def fromraw(obj):
        """Create an IndexedStl from an RawStl."""
        # pylint: disable=W0212
        nw = IndexedStl(obj.name)
        # Convert vertices and normals into a tuple of 3-tuples for fast
        # handling.
        vertices = tuple(i for a, b, c, _ in obj.facets for i in (a, b, c))
        normals = tuple(n for _, _, _, n in obj.facets)
        # Get the unique vertices and the indexed facets
        uniquevertices = sorted(set(vertices))
        vertexdict = {v: n for n, v in enumerate(uniquevertices)}
        vindices = tuple(vertexdict[v] for v in vertices)
        ifacets = [tuple(vindices[i:i+3]) for i in range(0, len(vindices), 3)]
        nw._vertices = list(uniquevertices)
        # Get the unique normals and all normal indices.
        uniquenormals = sorted(set(normals))
        normaldict = {v: n for n, v in enumerate(uniquenormals)}
        inormals = [normaldict[v] for v in normals]
        nw._normals = list(uniquenormals)
        nw._facets = [(a, b, c, n) for (a, b, c), n in zip(ifacets, inormals)]
        return nw

    def addfacet(self, f):
        """Add a facet to an IndexedStl.
        
        Argument:
        f -- a 3-tuple of 3-tuples
        """
        pass

    @property
    def numvertices(self):
        return len(self._vertices)

    @property
    def vertices(self):
        return tuple(self._vertices)

    @property
    def numnormals(self):
        return len(self._vertices)

    @property
    def normals(self):
        return tuple(self._normals)

    @property
    def numfacets(self):
        return len(self._facets)

    @property
    def facets(self):
        return tuple(self._facets)

    def bbox(self):
        """Return the BoundingBox of the object."""
        return bbox.make([p for p in self._vertices])

    def xform(self, m):
        """Transforms the indexed STL object."""
        newverts = [m.applyto(v) for v in self._vertices]
        newnormals = [n.applyrot(n) for n in self._normals]
        self._vertices = newverts
        self._normals = newnormals


if __name__ == '__main__':
    import stlfile
    from sys import argv
    if len(argv) < 2:
        print('usage: python', argv[0], 'filename')
        exit(1)
    rf = stlfile.StlReader(argv[1])
    print('Filename', rf.filename)
    print('Type:', rf.filetype)
    print('Number of facets:', rf.numfacets)
    raw = RawStl(rf.name)
    print('Reading', rf.filename)
    fcts = rf.readall()
    print('Adding facets to RawStl object.')
    degen = raw.addfacets(fcts)
    if degen:
        print(len(degen), 'degenerate facets found.')
        print(degen)
    print('----- begin RawSTL -----', raw, '----- end RawSTL -----', 
          sep = '\n')
    print('Creating indexed object...')
    indexed = IndexedStl.fromraw(raw)
    print('number of unique vertices:', indexed.numvertices)
    print('number of unique normals:', indexed.numnormals)
    print('----- begin IndexedSTL -----', indexed, 
          '----- end IndexedSTL -----', sep = '\n')

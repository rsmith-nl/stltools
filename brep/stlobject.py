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
from vector import normal, Vector3

__version__ = '$Revision$'[11:-2]

class RawStl(object):
    """A data representation of a raw STL file. Contains a combined list of
    facet vertices and normal vectors.
    """
    __slots__ = ['name', '_facets']

    def __init__(self, name):
        if name == None or len(name) == 0:
            name = 'unknown'
        self.name = name
        self._facets = []

    @property
    def facets(self):
        return tuple(self._facets)

    @property
    def numfacets(self):
        return len(self._facets)

    def __iter__(self):
        """Iterate over the facets of the RawStl.
        Each iteration receives a tuple (f,n) where f is a 3-tuple of Vector3
        objects contaiting the points of the facet, while n is the normal
        Vector3 of the facet.
        """
        return self._facets

    def addfacet(self, f):
        """Add a single facet to a RawStl.

        Arguments:
        f -- a 3-tuple of Vector3 objects

        Exceptions:
        ValueError -- when a degenerate facet is found.
        """
        assert isinstance(f, tuple) and len(f) == 3
        n = normal(f)
        if n.length == 0:
            raise ValueError('Degenerate facet found.')
        self._facets.append((f, n))

    def addfacets(self, lf):
        """Add a list of facets to a RawStl. Degenerate facets (with a
        0-length normal vector) are not added. But their indices in the lf
        array are returned.

        Arguments:
        lf -- a list of 3-tuples of Vector3 objects
        """
        comb = [(f, normal(f)) for f in lf]
        degenerates = [n for n, c in enumerate(comb) if c[1].length == 0]
        self._facets += [c for c in comb if c[1].length > 0]
        return degenerates


class IndexedStl(object):
    """In this representation, all the vertices and normal vectors are unique,
    and the facet list is a list of indices into the vertex and normal lists.
    """
    __slots__ = ['name', '_vertices', '_normals', '_facets']

    def __init__(self, name=''):
        self.name = name
        self._vertices = None
        self._normals = None
        self._facets = None

    @staticmethod
    def fromraw(obj):
        """Create an IndexedStl from an RawStl."""
        n = IndexedStl(obj.name)
        facets = obj.facets
        # Convert vertices and normals into a tuple of 3-tuples for fast
        # handling.
        vertices = tuple(i.coords for f in facets for i in f[0])
        normals = tuple(f[1].coords for f in facets)
        del facets
        # Get the unique vertices and the indexed facets
        uniquevertices = sorted(set(vertices))
        vertexdict = {v: n for n, v in enumerate(uniquevertices)}
        vindices = tuple(vertexdict[v] for v in vertices)
        ifacets = tuple(vindices[i:i+3] for i in range(0, len(vindices), 3))
        n._vertices = tuple(Vector3(*v) for v in uniquevertices)
        # Get the unique normals and all normal indices.
        uniquenormals = sorted(set(normals))
        normaldict = {v: n for n, v in enumerate(uniquenormals)}
        inormals = tuple(normaldict[v] for v in normals)
        n._normals = tuple(Vector3(*n) for n in uniquenormals)
        n._facets = zip(ifacets, inormals)
        return n

    @property
    def numvertices(self):
        return len(self._vertices)

    @property
    def vertices(self):
        return self._vertices

    @property
    def numnormals(self):
        return len(self._vertices)

    @property
    def normals(self):
        return self._normals

    @property
    def numfacets(self):
        return len(self._facets)

    @property
    def facets(self):
        return self._facets


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
    facets = rf.readall()
    print('Adding facets to RawStl object.')
    degen = raw.addfacets(facets)
    if degen:
        print(len(degen), 'degenerate facets found.')
        print(degen)
#    for num, facet in enumerate(rf):
#        try:
#            raw.addfacet(facet)
#        except ValueError:
#            print('Facet', num+1, 'is degenerate, skipping.')
#    print('Creating indexed object...')
    indexed = IndexedStl.fromraw(raw)
    print('number of facets:', indexed.numfacets)
    print('number of unique vertices:', indexed.numvertices)
    print('number of unique normals:', indexed.numnormals)


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

"""Manipulate STL models."""

from vector import normal

__version__ = '$Revision$'[11:-2]

class StlObject(object):
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
    def numfacets(self):
        return len(self._facets)

    def __iter__(self):
        """Iterate over the facets of the StlObject.
        Each iteration receives a tuple (f,n) where f is a 3-tuple of Vector3
        objects contaiting the points of the facet, while n is the normal
        Vector3 of the facet.
        """
        return self._facets

    def addfacet(self, f):
        """Add a facet to a StlObject.

        Arguments:
        f -- a 3-tuple of Vector3 objects

        Exceptions:
        ValueError is raised (by vector.normal) when a degenerate facet is
        found.
        """
        assert isinstance(f, tuple) and len(f) == 3
        n = normal(f)
        self._facets.append((f, n))


class IndexedStlObject(object):
    """In this representation, all the vertices and normal vectors are uniqu,
    and the facet list is a list of indices into the vertex and normal lists.
    """
    __slots__ = ['name', '_v', '_n', '_facets']

    def __init__(self, name=''):
        self.name = name
        self._v = []
        self._n = []
        self._facets = []

    @property
    def numfacets(self):
        return len(self._facets)

    def addfacet(self, f, n=None):
        """Add a facet to an IndexedStlObject.

        Arguments:
        f -- a 3-tuple of Vector3 objects

        Exceptions:
        ValueError is raised (by vector.normal) when a degenerate facet is
        found.
        """
        assert isinstance(f, tuple) and len(f) == 3
        if not n:
            n = normal(f)
        self._facets.append((f, n))

def find_unique_vertices(facets):
    vertices = [i.coords for f in facets for i in f]
    uniquevertices = sorted(set(vertices))
    vertexdict = {v: n for n, v in enumerate(uniquevertices)}
    indices = [vertexdict[v] for v in vertices]
    indexedfacets = [indices[i:i+3] for i in range(0, len(indices), 3)]
    return indexedfacets, uniquevertices


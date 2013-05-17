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

__version__ = '$Revision$'[11:-2]

class StlObject(object):
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
        return self._facets

    def addfacet(self, f):
        """Add a facet to a StlObject.

        Arguments:
        f -- a 3-tuple of Vector3 objects

        Exceptions:
        ValueError when a degenerate facet is found.
        """
        assert isinstance(f, tuple) and len(f) == 3
        n = normal(f)
        a, b, c = f
        self._facets.append((a, b, c, n))

def normal(f):
    """Calculate and return the normalized normal vector for the
    triangle defined by the vertices in the 3-tuple f.
    
    Arguments
    f -- 3-tuple of Vector3 objects

    Returns:
    The normal vector of the triangle formed by f

    Raises:
    ValueError when a 0-length normal is found.
    """
    a, b, c = f
    u = b - a
    v = c - b
    n = u.cross(v)
    L = n.length
    if L == 0:
        raise ValueError('degenerate facet')
    n = n/L
    return n


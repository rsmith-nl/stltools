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

# Check this code with 'pylint -r n vector.py'

"""Vector manipulation functions. Vectors are 3-tuples of floats."""

__version__ = '$Revision$'[11:-2]

from collections import namedtuple

class BoundingBox(object):

    def __init__(self, pnts):
        """Create a BoundingBox from a list of Vector3."""
        x = [p.x for p in pnts]
        y = [p.y for p in pnts]
        z = [p.z for p in pnts]
        self._minx, self._maxx = min(x), max(x)
        self._miny, self._maxy = min(y), max(y)
        self._minz, self._maxz = min(z), max(z)

    @property
    def minx(self):
        return self._minx

    @property
    def maxx(self):
        return self._maxx

    @property
    def miny(self):
        return self._miny

    @property
    def maxy(self):
        return self._maxy

    @property
    def minz(self):
        return self._minz

    @property
    def maxz(self):
        return self._maxz

    def center(self):
        return Vector3((self._minx + self._maxx)/2.0, 
                       (self._miny + self._maxy)/2.0,
                       (self._minz + self._maxz)/2.0)

    def length(self):
        return abs(self._maxx - self._minx)

    def width(self):
        return abs(self._maxy - self._miny)

    def height(self):
        return abs(self._maxz - self._minz)

    def volume(self):
        return self.length() * self.width() * self.height()


class Vector3(object):

    @staticmethod
    def _chkv(v):
        if not isinstance(v, Vector3):
            raise ValueError('argument must be a Vector3')

    def __init__(self, x, y=0.0, z=0.0):
        """Create a 3D vector."""
        if ((isinstance(x, list) or isinstance(x, tuple)) 
            and len(x) == 3):
            self._x, self._y, self._z = float(x[0]), float(x[1]), float(x[2])
        else:
            self._x, self._y, self._z = float(x), float(y), float(z)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    def __add__(self, other):
        """Return the sum of the 3D vectors self and other."""
        Vector3._chkv(other)
        return Vector3(self._x + other.x, self._y + other.y, 
                       self._z + other.z)

    def __sub__(self, other):
        """Return the difference of the 3D vectors self and other."""
        Vector3._chkv(other)
        return Vector3(self._x - other.x, self._y - other.y, 
                       self._z - other.z)

    def __mul__(self, scalar):
        """Return the 3D vector self multiplied with a scalar."""
        if isinstance(scalar, Vector3):
            raise NotImplementedError
        s = float(scalar)
        if s == 0:
            raise ValueError('would create a 0-length vector')
        return Vector3(self._x*s, self._y*s, self._z*s)

    def cross(self, other):
        '''Returns the cross product of two vectors.'''
        Vector3._chkv(other)
        return Vector3(self._y * other.z - self._z * other.y, 
                      self._z * other.x - self._x * other.z, 
                      self._x * other.y - self._y * other.x)

    def dot(self, other):
        '''Returns the dot- or scalar product.'''
        Vector3._chkv(other)
        return (self._x * other.x + self._y * other.y + self._z * other.z)

    def __div__(self, scalar):
        if isinstance(scalar, Vector3):
            raise NotImplementedError
        s = float(scalar)
        if s == 0:
            raise ValueError('division by 0')
        return Vector3(self._x/s, self._y/s, self._z/s)
    
    def __eq__(self, other):
        Vector3._chkv(other)
        return (self._x == other.x and self._y == other.y and 
                self._z == other.z) 

    def __ne__(self, other):
        Vector3._chkv(other)
        return (self._x != other.x or self._y != other.y or 
                self._z != other.z) 

    def length(self):
        return (self._x**2 + self._y**2 + self._z**2)**0.5

    def t(self):
        '''Returns a tuple of the Vector3 coordinates.'''
        return (self._x, self._y, self._z)


def normal(a, b, c):
    """Calculate and return the normalized normal vector for the
    triangle defined by the vertices a, b and c.
    
    Arguments
    a -- Vector3
    b -- Vector3
    v -- Vector3
    """
    u = b - a
    v = c - b
    n = u * v # Calculate the normal vector
    L = n.length()
    if L == 0.0:
        n = None
    else:
        n = n/L
    return n


def mean(pnts):
    """Calculate the mean of all pnts.

    Arguments:
    pnts -- list of Vector3 holding the point coordinates

    Returns
    A tuple (x,y,z)
    """
    L = len(pnts)
    x = [p.x for p in pnts]
    y = [p.y for p in pnts]
    z = [p.z for p in pnts]
    return Vector(sum(x)/L, sum(y)/L, sum(z)/L)


def lstindex(plst, p):
    """Check if points are in a list of points. If not, add them to the
    list. Return the indices of the found or added points.

    Arguments:
    plst -- list of Vectors holding the point coordinates
    p  -- Vector, or a list/tuple of them

    Returns
    a list of point indices.
    """
    if isinstance(p, Vector3): # single point
        p = [p]
    elif isinstance(p, tuple) or isinstance(p, list):
        pass
    else:
        raise ValueError('p should be a Vector3 or a list/tuple of them')
    ri = []
    for f in p:
        try:
            ri.append(plst.index(f))
        except ValueError:
            ri.append(len(plst))
            plst.append(f)
    return ri

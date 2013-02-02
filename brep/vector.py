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

def add(a, b):
    """Calculate and return a+b.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    """
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])


def sub(a, b):
    """Calculate and return a-b.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    """
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])


def cross(a, b):
    """Calculate and return the cross product of a and b.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    """
    return (a[1]*b[2] - a[2]*b[1], 
            a[2]*b[0] - a[0]*b[2], 
            a[0]*b[1] - a[1]*b[0])


def length(a):
    """Calculate and return the length of a.
    
    Arguments
    a -- 3-tuple of floats
    """
    return (a[0]**2 + a[1]**2 + a[2]**2)**0.5


def normal(a, b, c):
    """Calculate and return the normalized normal vector for the
    triangle defined by the vertices a, b and c.
    
    Arguments
    a -- 3-tuple of floats
    b -- 3-tuple of floats
    v -- 3-tuple of floats
    """
    u = sub(b, a)
    v = sub(c, b)
    n = cross(u, v) # Calculate the normal vector
    L = length(n)
    if L == 0.0:
        n = None
    else:
        n = (n[0]/L, n[1]/L, n[2]/L)
    return n


def normalize(a):
    """Calculate and return the normalized a.
    
    Arguments
    a -- 3-tuple of floats
    """
    L = (a[0]**2 + a[1]**2 + a[2]**2)**0.5
    if L == 0.0:
        raise ValueError('zero-length normal vector')
    return (a[0]/L, a[1]/L, a[2]/L)


def bbox(pnts):
    """Calculate the bounding box of all pnts.

    Arguments:
    pnts -- list of 3-tuples holding the point coordinates

    Returns
    A tuple (xmin, xmax, ymin, ymax, zmin, zmax)
    """
    x = [p[0] for p in pnts]
    y = [p[1] for p in pnts]
    z = [p[2] for p in pnts]
    return (min(x), max(x), min(y), max(y), min(z), max(z))


def mean(pnts):
    """Calculate the mean of all pnts.

    Arguments:
    pnts -- list of 3-tuples holding the point coordinates

    Returns
    A tuple (x,y,z)
    """
    x = [p[0] for p in pnts]
    y = [p[1] for p in pnts]
    z = [p[2] for p in pnts]
    return (sum(x)/len(x), sum(y)/len(y), sum(z)/len(z))


def lstindex(plst, p):
    """Check if points are in a list of points. If not, add them to the
    list. Return the indices of the found or added points.

    Arguments:
    plst -- list of 3-tuples holding the point coordinates
    p  -- 3-tuple holding the point, or a list/tuple of them

    Returns
    a list of point indices.
    """
    if isinstance(p[0], float) and len(p) == 3: # single point
        p = [p]
    elif isinstance(p[0], tuple) and len(p[0]) == 3:
        pass
    else:
        raise ValueError('p should be a 3-tuple or a iterable of 3-tuples')
    ri = []
    for f in p:
        try:
            ri.append(plst.index(f))
        except ValueError:
            ri.append(len(plst))
            plst.append(f)
    return ri

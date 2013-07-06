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

"""Operations of two or three dimensional vectors."""

def add(a, b):
    return tuple(i+j for i, j in zip(a, b))


def sub(a, b):
    return tuple(i-j for i, j in zip(a, b))


def mul(v, s):
    return tuple(s*j for j in v)


def div(v, s):
    return tuple(j/s for j in v)


def eq(a, b):
    return all(i==j for i, j in zip(a, b))


def ne(a, b):
    return any(i!=j for i, j in zip(a, b))


def length(v):
    return sum(j*j for j in v)**0.5


def normalize(v):
    l = length(v)
    return div(v, l)


def cross(a, b):
    if len(a) == 3 and len(b) == 3:
        ax, ay, az = a
        bx, by, bz = b
        return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)
    else:
        raise ValueError('cross product only defined for 3D vectors')


def dot(a, b):
    return sum(i*j for i, j in zip(a, b))


def mkstr(v, sep=', '):
    return sep.join(str(j) for j in v)


def normal(a, b, c):
    """Calculate the normal vector for the triangle defined by a, b and c.

    :a: 3-tuple of numbers
    :b: 3-tuple of numbers
    :c: 3-tuple of numbers
    :returns: a vector normal to the plane formed by a, b and c.
    """
    u = sub(b, a)
    v = sub(c, b)
    n = cross(u, v)
    l = length(n)
    if l:
        return div(n, l)
    return n


def indexate(points):
    """Convert a list of points into a list of indices and a list of unique
    points.

    :points: A list of points, where a point is a 3-tuple of numbers.
    :returns: A tuple (indices, unique_points)
    """
    pd = {}
    indices = [pd.setdefault(p, len(pd)) for p in points]
    pt = sorted([(v, k) for k, v in pd.iteritems()], key=lambda x: x[0])
    unique = [i[1] for i in pt]
    return indices, unique

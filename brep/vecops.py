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

import numpy as np
import math as m


def length(v):
    """Returns the length of a vector.

    :v: numpy vector
    """
    return m.sqrt(np.sum(v*v))


def normalize(v):
    """Returns the vector scaled to lenth 1.

    :v: numpy vector
    """
    l = length(v)
    return v/l


def normal(a, b, c):
    """Calculate the normal vector for the triangle defined by a, b and c.

    :a, b, c: numpy array of shape (3,)
    :returns: a vector normal to the plane formed by a, b and c.
    """
    u = b - a
    v = c - b
    n = np.cross(u, v)
    l = length(n)
    if l:
        return n/l
    return n


def indexate(points):
    """Convert a numpy array of points into a list of indices and an array of 
    unique points.

    :points: a numpy array of shape (N, 3)
    :returns: a tuple of indices and an array of unique points
    """
    pd = {}
    indices = tuple(pd.setdefault(tuple(p), len(pd)) for p in points)
    pt = sorted([(v, k) for k, v in pd.iteritems()], key=lambda x: x[0])
    unique = np.array([i[1] for i in pt])
    return indices, unique

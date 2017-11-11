# file: vecops.py
# vim:fileencoding=utf-8
#
# Copyright © 2013-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2013-06-10 22:41:00 +0200
# Last modified: 2017-06-04 16:44:10 +0200
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS "AS IS" AND
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
"""Operations on two or three dimensional vectors."""

import numpy as np
import math as m

__version__ = '5.0'


def length(v):
    """
    Calculate the length of a (N,) numpy array.

    Arguments:
        v: numpy array

    Returns:
        The length of the vector.
    """
    return m.sqrt(np.sum(v*v))


def normalize(v):
    """
    Scale the (N, ) array to lenth 1.

    Arguments:
        v: numpy array

    Returns:
        The scaled array.
    """
    ln = length(v)
    return v/ln


def normal(a, b, c):
    """
    Calculate the normal vector for the triangle defined by a, b and c.

    Arguments:
        a, b, c: Numpy arrays of shape (3,).

    Returns:
        A (3,) numpy array normal to the plane formed by a, b and c.
    """
    u = b - a
    v = c - b
    n = np.cross(u, v)
    ln = length(n)
    if ln:
        return n/ln
    return n


def indexate(points):
    """
    Create an array of unique points and indexes into this array.

    Arguments:
        points: A numpy array of shape (N, 3).

    Returns:
        An array of indices and an (M, 3) array of unique points.
    """
    pd = {}
    indices = [pd.setdefault(tuple(p), len(pd)) for p in points]
    pt = sorted([(v, k) for k, v in pd.items()], key=lambda x: x[0])
    unique = np.array([i[1] for i in pt])
    return np.array(indices, np.uint16), unique


def to4(pnts):
    """
    Convert 3D coordinates to homogeneous coordinates.

    Arguments:
        pnts: A numpy array of shape (N, 3).

    Returns:
        A numpy array of shape (N, 4).
    """
    if len(pnts.shape) != 2 or pnts.shape[1] != 3:
        raise ValueError('invalid shape')
    return np.hstack((pnts, np.ones(pnts.shape[0]).reshape((-1, 1))))


def to3(pnts):
    """
    Convert homogeneous coordinates to plain 3D coordinates.

    It scales the x, y and z values by the w value.

    Aruments:
        pnts: A numpy array of shape (N,4).

    Returns:
        A numpy array of shape (N,3).
    """
    if len(pnts.shape) != 2 or pnts.shape[1] != 4:
        raise ValueError('invalid shape')
    d = pnts[:, 3]
    div = np.vstack((d, d, d)).T
    return pnts[:, 0:3]/div


def xform(mat, pnts):
    """
    Apply a transformation matrix to a numpy array of points.

    Arguments:
        mat: A (3, 3) or (4, 4) numpy array.
        pnts: A (N,3) or (N,4) numpy array.

    Returns:
        The transformed array.
    """
    if len(pnts.shape) != 2 and pnts.shape[1] not in (3, 4):
        raise ValueError('wrong shape of pnts')
    conv = False
    if mat.shape == (3, 3):
        if pnts.shape[1] == 4:
            raise ValueError('homogeneous coordinates with 3x3 matrix')
    elif mat.shape == (4, 4):
        if pnts.shape[1] == 3:
            pnts = to4(pnts)
            conv = True
    else:
        raise ValueError('wrong shape of matrix')
    rv = np.array([np.dot(mat, v) for v in pnts])
    if conv:
        return to3(rv)
    return rv

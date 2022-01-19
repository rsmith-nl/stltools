# file: vecops.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2020 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2013-06-10 22:41:00 +0200
# Last modified: 2022-01-19T21:45:11+0100
"""Operations on two or three dimensional vectors."""


def length(v):
    """
    Calculate the length of a vector.

    Arguments:
        v: tuple of numbers

    Returns:
        The length of the vector.
    """
    return sum(j * j for j in v) ** 0.5


def normalize(v):
    """
    Scale the vector to lentgh 1.

    Arguments:
        v: tuple of numbers

    Returns:
        The scaled array.
    """
    ln = length(v)
    return tuple(j / ln for j in v)


def cross(u, v):
    """Create the cross-product of two 3-tuples u and v."""
    return tuple(
        [
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0],
        ]
    )


def normal(a, b, c):
    """
    Calculate the normal vector for the triangle defined by a, b and c.

    Arguments:
        a, b, c: 3-tuples of numbers

    Returns:
        A 3-tuple normal to the plane formed by a, b and c.
    """
    u = tuple(j - k for j, k in zip(b, a))
    v = tuple(j - k for j, k in zip(c, b))
    # cross product
    n = cross(u, v)
    try:
        return normalize(n)
    except ZeroDivisionError:
        return n


def indexate(points):
    """
    Create an array of unique points and indexes into this array.

    Here is an illustration of how it works;

    In [14]: points
    Out[14]:
    [(139.3592529296875, 97.01824951171875, 69.91365814208984),
    (138.14346313476562, 97.50768280029297, 70.0313949584961),
    (138.79571533203125, 97.875244140625, 69.03594970703125),
    (138.14346313476562, 97.50768280029297, 70.0313949584961),
    (139.3592529296875, 97.01824951171875, 69.91365814208984),
    (138.76876831054688, 96.6264419555664, 70.94448852539062),
    (138.79571533203125, 97.875244140625, 69.03594970703125),
    (138.14346313476562, 97.50768280029297, 70.0313949584961),
    (137.59768676757812, 98.35258483886719, 69.14176177978516),
    (139.3592529296875, 97.01824951171875, 69.91365814208984)]

    In [15]: pd = {}
    Out[15]: {}

    In [16]: indices = tuple(pd.setdefault(p, len(pd)) for p in points)
    Out[16]: (0, 1, 2, 1, 0, 3, 2, 1, 4, 0)

    In [17]: pd
    Out[17]:
    {(139.3592529296875, 97.01824951171875, 69.91365814208984): 0,
    (138.14346313476562, 97.50768280029297, 70.0313949584961): 1,
    (138.79571533203125, 97.875244140625, 69.03594970703125): 2,
    (138.76876831054688, 96.6264419555664, 70.94448852539062): 3,
    (137.59768676757812, 98.35258483886719, 69.14176177978516): 4}

    In [18]: tuple(pd.keys())
    Out[18]:
    ((139.3592529296875, 97.01824951171875, 69.91365814208984),
    (138.14346313476562, 97.50768280029297, 70.0313949584961),
    (138.79571533203125, 97.875244140625, 69.03594970703125),
    (138.76876831054688, 96.6264419555664, 70.94448852539062),
    (137.59768676757812, 98.35258483886719, 69.14176177978516))

    Arguments:
        points: A sequence of 3-tuples

    Returns:
        An array of indices and a sequence of unique 3-tuples.
    """
    pd = {}
    # Not only does this create a list of indices, but it also fills
    # the pd dict. And since dicts keep insertion order, pd.keys()
    # is a list of unique points
    indices = tuple(pd.setdefault(p, len(pd)) for p in points)
    return indices, tuple(pd.keys())


def to4(pnts):
    """
    Convert 3D coordinates to homogeneous coordinates.

    Arguments:
        pnts: A sequnce array of 3-tuples (x,y,z)

    Returns:
        A list of 4-tuples (x,y,z,1)
    """
    return tuple((p[0], p[1], p[2], 1) for p in pnts)


def to3(pnts):
    """
    Convert homogeneous coordinates to plain 3D coordinates.

    It scales the x, y and z values by the w value.

    Aruments:
        pnts: A sequence of 4-tuples (x,y,z,w)

    Returns:
        A list of 3-tuples (x,y,z)
    """
    return [(p[0] / p[3], p[1] / p[3], p[2] / p[3]) for p in pnts]


def xform(mat, pnts):
    """
    Apply a transformation matrix to a sequence of tuples.

    Arguments:
        mat: A 3×3 or 4×4 matrix in row-major order.
        pnts: A sequence of 3-tuples or 4-tuples of numbers.

    Returns:
        The transformed list of tuples.
    """
    mp = pnts
    r = len(mat[0])
    if r != len(pnts[0]):
        mp = to4(pnts)
    rv = []
    for p in mp:
        newp = []
        for j in range(4):
            newp.append(sum(i * k for i, k in zip(mat[j], p)))
        rv.append(tuple(newp))
    if len(pnts[0]) != len(rv[0]):
        return to3(rv)
    return rv

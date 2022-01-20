# file: test_vecops.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-06 23:26:45 +0200
# Last modified: 2020-10-03T22:54:32+0200
"""
Tests for the vecops module.

Run this test only with py.tests-3.5 -v test_vecops.py
Run all tests with: py.test-3.5 -v test_*
"""

import stltools.vecops as vo


def test_vo_length():
    # The 0-vector should have length 0.
    v = [0, 0, 0]
    assert vo.length(v) == 0
    # The unit vectors should all have length 1.
    v = [1, 0, 0]
    assert vo.length(v) == 1
    v = [0, 1, 0]
    assert vo.length(v) == 1
    v = [0, 0, 1]
    assert vo.length(v) == 1
    # (20**2+5**2+4**2)**0.5 == 21
    v = [20, 5, 4]
    assert vo.length(v) == 21


def test_vo_normalize():
    # The length of a normalized vector should be approximately 1.
    v = [20, 5, 4]
    r = vo.normalize(v)
    nom, tol = 1, 0.001
    assert nom - tol <= vo.length(r) <= nom + tol
    # The ratio of the components of the original and the normalized vector
    # should be the length of the original vector.
    assert all(i / j == 21 for i, j in zip(v, r))


def test_vo_normal():
    # The normal of a plane through the origin and two unit vectors should
    # be plus/minus other unit vector.
    r = vo.normal([0, 0, 0], [1, 0, 0], [0, 1, 0])
    assert all(i == j for i, j in zip(r, [0, 0, 1]))
    r = vo.normal([0, 0, 0], [0, 0, 1], [1, 0, 0])
    assert all(i == j for i, j in zip(r, [0, 1, 0]))
    r = vo.normal([0, 0, 0], [0, 1, 0], [0, 0, 1])
    assert all(i == j for i, j in zip(r, [1, 0, 0]))
    # The components of the normal of a plane through the three unit vectors
    # should all be 1/√3.
    r = vo.normal([1, 0, 0], [0, 1, 0], [0, 0, 1])
    c = 1 / (3 ** 0.5)
    assert all(i == j for i, j in zip(r, [c, c, c]))


def test_vo_indexate():
    # Create 5 unique points and then make a list of 10 point by concatenating
    # that twice. Indexing that should give the indexes 0, 1, 2, 3, 4 twice,
    # and the five unique points.
    c = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14))
    pnts = 2 * c
    q = list(range(5)) * 2
    indices, unique = vo.indexate(pnts)
    assert indices == tuple(q)
    assert unique == c


def test_vo_to():
    pnts = [
        [0.0, 1.0, 2.0],
        [3.0, 4.0, 5.0],
        [6.0, 7.0, 8.0],
        [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0],
    ]
    p4 = vo.to4(pnts)
    # The last component of all homogeneous vectors should be 1.
    assert all(p[3] == 1 for p in p4)
    # The operation should be reversible.
    p3 = vo.to3(p4)
    for p, q in zip(pnts, p3):
        assert all(i == j for i, j in zip(p, q))

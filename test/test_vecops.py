# file: test_vecops.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-06 23:26:45 +0200
# Last modified: 2016-06-11 00:46:27 +0200

"""
Tests for the vecops module.

Run this test only with py.tests-3.5 -v test_vecops.py
Run all tests with: py.test-3.5 -v test_*
"""

import numpy as np
import stltools.vecops as vo


def test_vo_length():
    # The 0-vector should have length 0.
    v = np.array([0, 0, 0])
    assert vo.length(v) == 0
    # The unit vectors should all have length 1.
    v = np.array([1, 0, 0])
    assert vo.length(v) == 1
    v = np.array([0, 1, 0])
    assert vo.length(v) == 1
    v = np.array([0, 0, 1])
    assert vo.length(v) == 1
    # (20**2+5**2+4**2)**0.5 == 21
    v = np.array([20, 5, 4])
    assert vo.length(v) == 21


def test_vo_normalize():
    # The length of a normalized vector should ba approximately 1.
    v = np.array([20, 5, 4])
    r = vo.normalize(v)
    nom, tol = 1, 0.001
    assert nom - tol <= vo.length(r) <= nom + tol
    # The ratio of the components of the original and the normalized vector
    # should be the length of the original vector.
    assert np.all(v/r == 21)


def test_vo_normal():
    # The normal of a plane through the origin and two unit vectors should
    # be plus/minus other unit vector.
    r = vo.normal(np.array([0, 0, 0]), np.array([1, 0, 0]),
                  np.array([0, 1, 0]))
    assert np.all(r == np.array([0, 0, 1]))
    r = vo.normal(np.array([0, 0, 0]), np.array([0, 0, 1]),
                  np.array([1, 0, 0]))
    assert np.all(r == np.array([0, 1, 0]))
    r = vo.normal(np.array([0, 0, 0]), np.array([0, 1, 0]),
                  np.array([0, 0, 1]))
    assert np.all(r == np.array([1, 0, 0]))
    # The components of the normal of a plane through the three unit vectors
    # should all be 1/√3.
    r = vo.normal(np.array([1, 0, 0]), np.array([0, 1, 0]),
                  np.array([0, 0, 1]))
    c = 1/(3**0.5)
    assert np.all(r == np.array([c, c, c]))


def test_vo_indexate():
    # Create 5 unique points and then make a list of 10 point by concatenating
    # that twice. Indexing that should give the indexes 0, 1, 2, 3, 4 twice,
    # and the five unique points.
    c = np.arange(15).reshape((-1, 3))
    pnts = np.concatenate((c, c))
    q = np.arange(5, dtype=np.uint16)
    q = np.concatenate((q, q))
    indices, unique = vo.indexate(pnts)
    assert np.all(unique == c)
    assert np.all(indices == q)


def test_vo_to():
    pnts = np.arange(15).reshape((-1, 3))
    p4 = vo.to4(pnts)
    # The last component of all homogeneous vectors should be 1.
    assert np.all(p4[:, 3] == 1)
    # The operation should be reversible.
    p3 = vo.to3(p4)
    assert np.all(p3 == pnts)

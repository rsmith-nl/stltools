# file: test_matrix.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-06 23:26:45 +0200
# Last modified: 2016-06-11 00:43:29 +0200

"""
Tests for the matrix module.

Run this test only with py.test-3.5 -v test_matrix.py
Run all tests with: py.test-3.5 -v test_*
"""

import numpy as np
import stltools.vecops as vo
import stltools.matrix as ma


def test_vo_xform_scale():
    m = np.identity(4)*0.5
    m[-1, -1] = 1.0
    pnts = np.arange(15).reshape((-1, 3))
    r = vo.xform(m, pnts)
    assert np.all(r*2 == pnts)
    p = ma.scale(0.5, 0.5, 0.5)
    r = vo.xform(p, pnts)
    assert np.all(r*2 == pnts)


def test_vo_xform_trans():
    m = np.identity(4)
    m.T[-1] = np.array([2, 3, 4, 1.0])
    pnts = np.arange(15).reshape((-1, 3))
    r = vo.xform(m, pnts)
    q = np.array([2, 3, 4]*5).reshape((-1, 3))
    assert np.all(r - q == pnts)
    m = ma.trans(np.array([2, 3, 4]))
    r = vo.xform(m, pnts)
    assert np.all(r - q == pnts)


def test_xform_rotx():
    m = ma.rotx(120)
    pnts = np.arange(15).reshape((-1, 3))
    r = vo.xform(m, pnts)
    s = vo.xform(m, r)
    t = vo.xform(m, s)
    print(t)
    print(pnts)
    assert np.all(t - pnts < 0.001)


def test_xform_roty():
    m = ma.roty(120)
    pnts = np.arange(15).reshape((-1, 3))
    r = vo.xform(m, pnts)
    s = vo.xform(m, r)
    t = vo.xform(m, s)
    assert np.all(t - pnts < 0.001)


def test_xform_rotz():
    m = ma.rotz(120)
    pnts = np.arange(15).reshape((-1, 3))
    print(pnts)
    r = vo.xform(m, pnts)
    s = vo.xform(m, r)
    t = vo.xform(m, s)
    assert np.all(t - pnts < 0.001)

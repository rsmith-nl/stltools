# file: test-stltools.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-06 23:26:45 +0200
# $Date$
# $Revision$

"""Tests for the stltools module.

Run with: nosetests-3.4 -v test-stltools.py
"""

import os
import sys

bp = os.path.dirname(os.path.realpath('.')).split(os.sep)
modpath = os.sep.join(bp + ['stltools'])
sys.path.append(modpath)

import numpy as np
import vecops as vo
import matrix as ma


def test_vo_length():
    v = np.array([0, 0, 0])
    assert vo.length(v) == 0
    v = np.array([1, 0, 0])
    assert vo.length(v) == 1
    v = np.array([0, 1, 0])
    assert vo.length(v) == 1
    v = np.array([0, 0, 1])
    assert vo.length(v) == 1
    v = np.array([20, 5, 4])
    assert vo.length(v) == 21


def test_vo_normalize():
    v = np.array([20.0, 5.0, 4.0])
    r = vo.normalize(v)
    assert np.all(v/r == 21)


def test_vo_normal():
    r = vo.normal(np.array([0, 0, 0]), np.array([1, 0, 0]),
                  np.array([0, 1, 0]))
    assert np.all(r == np.array([0, 0, 1]))


def test_vo_indexate():
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
    p3 = vo.to3(p4)
    assert np.all(p3 == pnts)


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

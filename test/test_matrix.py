# file: test_matrix.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-06 23:26:45 +0200
# Last modified: 2020-10-03T23:42:41+0200
"""
Tests for the matrix module.

Run this test only with py.test-3.5 -v test_matrix.py
Run all tests with: py.test-3.5 -v test_*
"""

import stltools.vecops as vo
import stltools.matrix as ma


def test_vo_xform_scale():
    m = ma.I()
    for j in range(3):
        m[j][j] = 0.5
    pnts = [
        [0.0,  1.0,  2.0], [3.0,  4.0,  5.0], [6.0,  7.0,  8.0], [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0]
    ]
    r = vo.xform(m, pnts)
    assert all(all(2*p == q for p, q in zip(i, j)) for i, j in zip(r, pnts))
    p = ma.scale(0.5, 0.5, 0.5)
    r = vo.xform(p, pnts)
    assert all(all(2*p == q for p, q in zip(i, j)) for i, j in zip(r, pnts))


def test_vo_xform_trans():
    m = ma.I()
    m[0][3] = 2
    m[1][3] = 3
    m[2][3] = 4
    pnts = [
        [0.0,  1.0,  2.0], [3.0,  4.0,  5.0], [6.0,  7.0,  8.0], [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0]
    ]
    r = vo.xform(m, pnts)
    q = [[2, 3, 4]] * 5
    assert all(all(a - b == c for a, b, c in zip(i, j, k)) for i, j, k in zip(r, q, pnts))
    m = ma.trans([2, 3, 4])
    r = vo.xform(m, pnts)
    assert all(all(a - b == c for a, b, c in zip(i, j, k)) for i, j, k in zip(r, q, pnts))


def test_xform_rotx():
    m = ma.rotx(120)
    pnts = [
        [0.0,  1.0,  2.0], [3.0,  4.0,  5.0], [6.0,  7.0,  8.0], [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0]
    ]
    r = vo.xform(m, pnts)
    s = vo.xform(m, r)
    t = vo.xform(m, s)
    print(t)
    print(pnts)
    assert all(all(p - q < 0.001 for p, q in zip(i, j)) for i, j in zip(t, pnts))


def test_xform_roty():
    m = ma.roty(120)
    pnts = [
        [0.0,  1.0,  2.0], [3.0,  4.0,  5.0], [6.0,  7.0,  8.0], [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0]
    ]
    r = vo.xform(m, pnts)
    s = vo.xform(m, r)
    t = vo.xform(m, s)
    assert all(all(p - q < 0.001 for p, q in zip(i, j)) for i, j in zip(t, pnts))


def test_xform_rotz():
    m = ma.rotz(120)
    pnts = [
        [0.0,  1.0,  2.0], [3.0,  4.0,  5.0], [6.0,  7.0,  8.0], [9.0, 10.0, 11.0],
        [12.0, 13.0, 14.0]
    ]
    print(pnts)
    r = vo.xform(m, pnts)
    s = vo.xform(m, r)
    t = vo.xform(m, s)
    assert all(all(p - q < 0.001 for p, q in zip(i, j)) for i, j in zip(t, pnts))

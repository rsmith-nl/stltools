# file: test_stl.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-08-22 16:45:36 +0200
# Last modified: 2017-08-22 22:36:28 +0200

"""
Tests for the stl module.

Run this test only with py.test-3.5 -v test_stl.py
Run all tests with: py.test-3.5 -v test_*
"""

import numpy as np
import stltools.stl as stl


def test_read_bin():
    vertices, name = stl.readstl('data/cube-bin.stl')
    assert name == 'cube_bin'
    assert vertices.shape == (36, 3)
    _, pnts = stl.toindexed(vertices)
    assert pnts.shape == (8, 3)


def test_read_txt():
    vertices, name = stl.readstl('data/cube-txt.stl')
    assert name == 'cube_txt'
    assert vertices.shape == (36, 3)
    _, pnts = stl.toindexed(vertices)
    assert pnts.shape == (8, 3)
    assert np.all(pnts[0] == np.array([0,  0,  1]))
    assert np.all(pnts[1] == np.array([1,  0,  1]))
    assert np.all(pnts[2] == np.array([0,  1,  1]))
    assert np.all(pnts[3] == np.array([1,  1,  1]))
    assert np.all(pnts[4] == np.array([1,  0,  0]))
    assert np.all(pnts[5] == np.array([0,  0,  0]))
    assert np.all(pnts[6] == np.array([1,  1,  0]))
    assert np.all(pnts[7] == np.array([0,  1,  0]))


def test_normals():
    vertices, name = stl.readstl('data/cube-txt.stl')
    facets, pnts = stl.toindexed(vertices)
    ni, nv = stl.normals(facets, pnts)
    assert len(ni) == 12  # 6 faces, 2 facets/face.
    p = np.arange(6)
    assert np.all(ni == np.vstack((p, p)).T.reshape((1, -1)))
    assert nv.shape == (6, 3)


def test_text():
    vertices, name = stl.readstl('data/cube-txt.stl')
    facets, pnts = stl.toindexed(vertices)
    ni, nv = stl.normals(facets, pnts)
    res = stl.text('cube_txt', facets, pnts, ni, nv)
    res = [ln.strip() for ln in res.splitlines()]
    with open('data/cube-txt.stl') as inp:
        orig = [ln.strip() for ln in inp.readlines()]
    for a, b in zip(orig, res):
        assert a == b

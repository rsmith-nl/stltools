# file: test_stl.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-08-22 16:45:36 +0200
# Last modified: 2020-10-04T14:31:00+0200
"""
Tests for the stl module.

Run this test only with py.test-v test_stl.py
Run all tests with: py.test -v test_*
"""

import stltools.stl as stl


def test_read_bin():
    vertices, name = stl.readstl('test/data/cube-bin.stl')
    assert name == 'cube_bin'
    assert len(vertices) == 36 and len(vertices[0]) == 3
    _, pnts = stl.toindexed(vertices)
    assert len(pnts) == 8 and len(pnts[0]) == 3


def test_read_txt():
    vertices, name = stl.readstl('test/data/cube-txt.stl')
    assert name == 'cube_txt'
    assert len(vertices) == 36 and len(vertices[0]) == 3
    _, pnts = stl.toindexed(vertices)
    assert len(pnts) == 8 and len(pnts[0]) == 3
    assert all(i == j for i, j in zip(pnts[0], [0, 0, 1]))
    assert all(i == j for i, j in zip(pnts[1], [1, 0, 1]))
    assert all(i == j for i, j in zip(pnts[2], [0, 1, 1]))
    assert all(i == j for i, j in zip(pnts[3], [1, 1, 1]))
    assert all(i == j for i, j in zip(pnts[4], [1, 0, 0]))
    assert all(i == j for i, j in zip(pnts[5], [0, 0, 0]))
    assert all(i == j for i, j in zip(pnts[6], [1, 1, 0]))
    assert all(i == j for i, j in zip(pnts[7], [0, 1, 0]))


def test_normals():
    vertices, name = stl.readstl('test/data/cube-txt.stl')
    facets, pnts = stl.toindexed(vertices)
    ni, nv = stl.normals(facets, pnts)
    assert len(ni) == 12  # 6 faces, 2 facets/face.
    assert all(i == j for i, j in zip(ni, [p for p in range(6) for k in range(2)]))
    assert len(nv) == 6 and len(nv[0]) == 3


def test_text():
    origpath = 'test/data/cube-txt.stl'
    vertices, name = stl.readstl(origpath)
    facets, pnts = stl.toindexed(vertices)
    ni, nv = stl.normals(facets, pnts)
    res = stl.text('cube_txt', facets, pnts, ni, nv)
    res = [' '.join(ln.strip().split()) for ln in res.splitlines()]
    with open(origpath) as inp:
        orig = [' '.join(ln.strip().split()) for ln in inp.readlines()]
    for a, b in zip(orig, res):
        assert a == b

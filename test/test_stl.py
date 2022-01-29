# file: test_stl.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-08-22 16:45:36 +0200
# Last modified: 2022-01-20T09:32:36+0100
"""
Tests for the stl module.

Run this test only with py.test-v test_stl.py
Run all tests with: py.test -v test_*
"""

import stltools.stl as stl


def test_toindexed():
    points = (
        (139.3592529296875, 97.01824951171875, 69.91365814208984),
        (138.14346313476562, 97.50768280029297, 70.0313949584961),
        (138.79571533203125, 97.875244140625, 69.03594970703125),
        (138.14346313476562, 97.50768280029297, 70.0313949584961),
        (139.3592529296875, 97.01824951171875, 69.91365814208984),
        (138.76876831054688, 96.6264419555664, 70.94448852539062),
        (138.79571533203125, 97.875244140625, 69.03594970703125),
        (138.14346313476562, 97.50768280029297, 70.0313949584961),
        (137.59768676757812, 98.35258483886719, 69.14176177978516),
        (139.3592529296875, 97.01824951171875, 69.91365814208984),
        (138.79571533203125, 97.875244140625, 69.03594970703125),
        (139.86764526367188, 97.37857055664062, 69.00691223144531),
    )
    sollfacets = ((0, 1, 2), (1, 0, 3), (2, 1, 4), (0, 2, 5))
    sollpoints = (
        (139.3592529296875, 97.01824951171875, 69.91365814208984),
        (138.14346313476562, 97.50768280029297, 70.0313949584961),
        (138.79571533203125, 97.875244140625, 69.03594970703125),
        (138.76876831054688, 96.6264419555664, 70.94448852539062),
        (137.59768676757812, 98.35258483886719, 69.14176177978516),
        (139.86764526367188, 97.37857055664062, 69.00691223144531),
    )
    istfacets, istpoints = stl.toindexed(points)
    assert sollfacets == istfacets
    assert sollpoints == istpoints


def test_read_bin():
    vertices, name = stl.readstl("test/data/cube-bin.stl")
    assert name == "cube_bin"
    assert len(vertices) == 36 and len(vertices[0]) == 3
    _, pnts = stl.toindexed(vertices)
    assert len(pnts) == 8 and len(pnts[0]) == 3


def test_read_txt():
    vertices, name = stl.readstl("test/data/cube-txt.stl")
    assert name == "cube_txt"
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
    vertices, name = stl.readstl("test/data/cube-txt.stl")
    facets, pnts = stl.toindexed(vertices)
    ni, nv = stl.normals(facets, pnts)
    assert len(ni) == 12  # 6 faces, 2 facets/face.
    assert all(i == j for i, j in zip(ni, [p for p in range(6) for k in range(2)]))
    assert len(nv) == 6 and len(nv[0]) == 3


def test_text():
    origpath = "test/data/cube-txt.stl"
    vertices, name = stl.readstl(origpath)
    facets, pnts = stl.toindexed(vertices)
    ni, nv = stl.normals(facets, pnts)
    res = stl.text("cube_txt", facets, pnts, ni, nv)
    res = [" ".join(ln.strip().split()) for ln in res.splitlines()]
    with open(origpath) as inp:
        orig = [" ".join(ln.strip().split()) for ln in inp.readlines()]
    for a, b in zip(orig, res):
        assert a == b

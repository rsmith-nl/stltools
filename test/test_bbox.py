# file: test_bbox.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2020-10-04T12:09:51+0200
# Last modified: 2020-10-04T13:08:36+0200

import stltools.bbox as bbox


def test_bbox2():
    pnts = [(83, -24), (89, 60), (19, -2), (-3, -90), (-8, 15), (96, 14), (11, 49)]
    x = [p[0] for p in pnts]
    y = [p[1] for p in pnts]
    b = bbox.makebb(pnts)
    assert min(x) == b[0]
    assert max(x) == b[1]
    assert min(y) == b[2]
    assert max(y) == b[3]


def test_inside2():
    pnts = [(83, -24), (89, 60), (19, -2), (-3, -90), (-8, 15), (96, 14), (11, 49)]
    b = bbox.makebb(pnts)
    assert bbox.inside(b, (4, 25)) == True  # noqa
    assert bbox.inside(b, (-20, 75)) == False  # noqa
    assert bbox.inside(b, (100, 75)) == False  # noqa
    assert bbox.inside(b, (4, -150)) == False  # noqa
    assert bbox.inside(b, (4, 150)) == False  # noqa


def test_bbox3():
    pnts = [
        (-2, -26, 83),
        (-100, -64, 87),
        (73, 77, 24),
        (40, 56, -50),
        (-71, 31, -43),
        (78, 29, 99),
        (87, -93, -35),
    ]
    x = [p[0] for p in pnts]
    y = [p[1] for p in pnts]
    z = [p[2] for p in pnts]
    b = bbox.makebb(pnts)
    assert min(x) == b[0]
    assert max(x) == b[1]
    assert min(y) == b[2]
    assert max(y) == b[3]
    assert min(z) == b[4]


def test_insider3():
    pnts = [
        (-2, -26, 83),
        (-100, -64, 87),
        (73, 77, 24),
        (40, 56, -50),
        (-71, 31, -43),
        (78, 29, 99),
        (87, -93, -35),
    ]
    b = bbox.makebb(pnts)
    assert bbox.inside(b, (4, 25, 0)) == True  # noqa
    assert bbox.inside(b, (-120, 75, 0)) == False  # noqa
    assert bbox.inside(b, (100, 75, 0)) == False  # noqa
    assert bbox.inside(b, (4, -150, 0)) == False  # noqa
    assert bbox.inside(b, (4, 150, 0)) == False  # noqa
    assert bbox.inside(b, (4, 25, -60)) == False  # noqa
    assert bbox.inside(b, (4, 25, 125)) == False  # noqa

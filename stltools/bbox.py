# file: bbox.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2020 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2013-06-10 22:41:00 +0200
# Last modified: 2020-10-04T12:14:22+0200
"""Operations on two or three dimensional bounding boxes."""


def makebb(pnts):
    """
    Find the bounding box for a list of points.

    Arguments:
        pnts: Sequence of 2-tuples or 3-tuples

    Returns:
        A list [minx, maxx, miny, maxy[, minz, maxz]].
    """
    x = [p[0] for p in pnts]
    y = [p[1] for p in pnts]
    rv = [min(x), max(x), min(y), max(y)]
    if len(pnts[0] == 3):
        z = [p[2] for p in pnts]
        rv += [min(z), max(z)]
    return rv


def inside(bb, v):
    """
    Test if a point is inside a bounding box.

    Arguments:
        bb: Bounding box list [minx, maxx, miny, maxy[, minz, maxz]].
        v: 3-tuple

    Returns:
        True if v is inside the bounding box, false otherwise.

    Raises:
        ValueError if the number of dimensions of the point and bounding box
        don't match.
    """
    rv = (bb[0] <= v[0] <= bb[1]) and (bb[2] <= v[1] <= bb[3])
    if len(bb) == 6 and len(v) == 3:
        return rv and (bb[4] <= v[2] <= bb[5])
    elif len(bb) == 4 and len(v) == 2:
        return rv
    else:
        raise ValueError('bbox and v must both be 2D or 3D')

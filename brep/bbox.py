# -*- coding: utf-8 -*-
# Copyright © 2013 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""Operations on two or three dimensional bounding boxes."""


def make(lv):
    if len(lv[0]) == 3:
        x, y, z = zip(*lv)
        return min(x), max(x), min(y), max(y), min(z), max(z)
    elif len(lv[0]) == 2:
        x, y = zip(*lv)
        return min(x), max(x), min(y), max(y)


def inside(bb, v):
    if len(bb) == 6 and len(v) == 3:
        vx, vy, vz = v
        minx, maxx, miny, maxy, minz, maxz = bb
        return (minx <= vx <= maxx and miny <= vy <= maxy and 
                minz <= vz <= maxz)
    elif len(bb) == 4 and len(v) == 2:
        vx, vy = v
        minx, maxx, miny, maxy = bb
        return minx <= vx <= maxx and miny <= vy <= maxy
    raise ValueError('wrong box/vector combo')


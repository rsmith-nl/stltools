# -*- coding: utf-8 -*-
# Classes for handling coordinate transforms and projections.
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Time-stamp: <2011-10-15 18:12:14 rsmith>
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

import math


class Zpar:
    '''Class for parallel projection along the Z-axis. Output
       screen coordinates from left top, size 100×100 mm.'''

    def __init__(self, xmin, xmax, ymin, ymax):
        '''Initialize the projection for an object in the rectangle, 
           xmin, xmax, ymin, ymax, to the target window.'''
        # 100 mm is 100/25.4*72 = 283.46457 PostScript points
        self.s = min(283.46457/(xmax-xmin), 283.46457/(ymax-ymin))
        self.xmin = xmin
        self.ymin = ymin
        self.ymax = ymax
        self.w = math.ceil(self.s*(xmax-xmin))
        self.h = math.ceil(self.s*(ymax-ymin))
        self.horg = ymax-ymin
        self.xo = self.w/2
        self.yo = self.h/2 

    def project(self, x, y, z):
        '''Transforms a vector x,y,z. Returns an (x,y) tuple'''
        rx = (x-self.xmin)*self.s
        ry = (self.horg-(y-self.ymin))*self.s
        return (rx, ry)

    def visible(self, x, y, z):
        '''Checks a normal vector x,y,z to see if it points toward or away
           from the viewer. Returns True in the first case.'''
        if (z > 0.0): 
            return True
        return False


_limit = 1e-7


def _unity():
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def _mmul(m1, m2):
    r = _unity()
    for i in range(3):
        for j in range(3):
            r[i][j] = m1[i][0]*m2[0][j] + m1[i][1]*m2[1][j] + m1[i][2]*m2[2][j]
            if math.fabs(r[i][j]) < _limit: 
                r[i][j] = 0.0
    return r


class Xform:
    '''Class for coordinate transformations in the form of rotations around
       the axis.'''

    def __init__(self):
        '''Initialize the transformation to the unity transform.'''
        self.reset()

    def __eq__(self, other):
        '''Check if two transformations are equal'''
        for i in range(3):
            for j in range(3):
                if math.fabs(self.m[i][j] - other.m[i][j]) > _limit:
                    return False
        return True

    def reset(self):
        '''Reverts to the unity transformation.'''
        self.m = _unity()
        self.unity = True

    def rotx(self, deg):
        '''Adds a rotation around the x-axis to the transformation.'''
        self.unity = False
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        add = [[1.0, 0.0, 0.0],
               [0.0,   c,  -s],
               [0.0,   s,   c]]
        self.m = _mmul(add, self.m)

    def roty(self, deg):
        '''Adds a rotation around the y-axis to the transformation.'''
        self.unity = False
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        add = [[  c, 0.0,   s],
               [0.0, 1.0, 0.0],
               [ -s, 0.0,   c]]
        self.m = _mmul(add, self.m)

    def rotz(self, deg):
        '''Adds a rotation around the z-axis to the transformation.'''
        self.unity = False
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        add = [[  c,  -s, 0.0],
               [  s,   c, 0.0],
               [0.0, 0.0, 1.0]]
        self.m = _mmul(add, self.m)

    def apply(self, x, y, z):
        '''Apply the transformation to point x,y,z and return the transformed
           coordinates as a tuple.'''
        xr = self.m[0][0]*x + self.m[0][1]*y + self.m[0][2]*z
        yr = self.m[1][0]*x + self.m[1][1]*y + self.m[1][2]*z
        zr = self.m[2][0]*x + self.m[2][1]*y + self.m[2][2]*z
        return (xr, yr, zr)


# Built-in tests.
if __name__ == '__main__':
    tr = Xform()
    print "Original matrix:", tr.m
    tr.rotx(45) 
    tr.rotx(-45)
    print "rotation 45,-45° around X:", tr.m
    tr.rotx(45)
    tr.rotx(315)
    print "rotation 45,315° around X:", tr.m
    tr.roty(30)
    tr.roty(-30)
    print "rotation 30,-30° around Y:", tr.m
    tr.roty(30)
    tr.roty(330)
    print "rotation 30,330° around Y:", tr.m
    tr.rotz(90)
    tr.rotz(-90)
    print "rotation 90,-90° around Z:", tr.m
    tr.rotz(90)
    tr.rotz(270)
    print "rotation 90,270° around Z:", tr.m
    tr.reset()
    tr.rotx(90)
    res = tr.apply(0, 1, 0)
    print "(0,1,0) rotated 90° around X:", res
    tr.reset()
    tr.roty(90)
    res = tr.apply(0, 0, 1)
    print "(0,0,1) rotated 90° around Y:", res
    tr.reset()
    tr.rotz(90)
    res = tr.apply(1, 0, 0)
    print "(1,0,0) rotated 90° around Z:", res

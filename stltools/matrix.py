# file: matrix.py
# vim:fileencoding=utf-8
#
# Copyright © 2013-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2013-07-28 02:07:00 +0200
# Last modified: 2020-10-03T23:54:25+0200
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
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS "AS IS" AND
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
"""
3D homogeneous coordinates matrix functions.

For a right-handed coordinate system.
"""

import math
import stltools.vecops as vo


def I():  # noqa
    """
    Create identity matrix.

    Returns:
        A 4x4 row-major matrix.
    """
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def trans(vec):
    """
    Create a transformation matrix for translation.

    Arguments:
        vec: 3-tuple representing a 3D translation vector.

    Returns:
        A 4x4 row-major matrix.
    """
    rv = I()
    rv[0][3] = vec[0]
    rv[1][3] = vec[1]
    rv[2][3] = vec[2]
    return rv


def mul(*args):
    """
    Return the multiplication of the 4x4 matrix arguments.

    Arguments:
        args: 4x4 numpy arrayis of float32 A, B, C, ..., N.

    Returns:
        A × B × C × ... × N
    """


def dot(a, b):
    """Returns the product of the two row-major matrices a and b."""
    rv = I()
    # first row
    rv[0][0] = a[0][0]*b[0][0] + a[0][1]*b[1][0] + a[0][2]*b[2][0] + a[0][3]*b[3][0]
    rv[0][1] = a[0][0]*b[0][1] + a[0][1]*b[1][1] + a[0][2]*b[2][1] + a[0][3]*b[3][1]
    rv[0][2] = a[0][0]*b[0][2] + a[0][1]*b[1][2] + a[0][2]*b[2][2] + a[0][3]*b[3][2]
    rv[0][3] = a[0][0]*b[0][3] + a[0][1]*b[1][3] + a[0][2]*b[2][3] + a[0][3]*b[3][3]
    # second row
    rv[1][0] = a[1][0]*b[0][0] + a[1][1]*b[1][0] + a[1][2]*b[2][0] + a[1][3]*b[3][0]
    rv[1][1] = a[1][0]*b[0][1] + a[1][1]*b[1][1] + a[1][2]*b[2][1] + a[1][3]*b[3][1]
    rv[1][2] = a[1][0]*b[0][2] + a[1][1]*b[1][2] + a[1][2]*b[2][2] + a[1][3]*b[3][2]
    rv[1][3] = a[1][0]*b[0][3] + a[1][1]*b[1][3] + a[1][2]*b[2][3] + a[1][3]*b[3][3]
    # third row
    rv[2][0] = a[2][0]*b[0][0] + a[2][1]*b[1][0] + a[2][2]*b[2][0] + a[2][3]*b[3][0]
    rv[2][1] = a[2][0]*b[0][1] + a[2][1]*b[1][1] + a[2][2]*b[2][1] + a[2][3]*b[3][1]
    rv[2][2] = a[2][0]*b[0][2] + a[2][1]*b[1][2] + a[2][2]*b[2][2] + a[2][3]*b[3][2]
    rv[2][3] = a[2][0]*b[0][3] + a[2][1]*b[1][3] + a[2][2]*b[2][3] + a[2][3]*b[3][3]
    # fourth row
    rv[3][0] = a[3][0]*b[0][0] + a[3][1]*b[1][0] + a[3][2]*b[2][0] + a[3][3]*b[3][0]
    rv[3][1] = a[3][0]*b[0][1] + a[3][1]*b[1][1] + a[3][2]*b[2][1] + a[3][3]*b[3][1]
    rv[3][2] = a[3][0]*b[0][2] + a[3][1]*b[1][2] + a[3][2]*b[2][2] + a[3][3]*b[3][2]
    rv[3][3] = a[3][0]*b[0][3] + a[3][1]*b[1][3] + a[3][2]*b[2][3] + a[3][3]*b[3][3]
    return rv


def concat(*args):
    """
    Concatenate the transforms.

    This is actually a multiplication of the arguments in reversed order.

    Arguments:
        args: 4x4 arrays of float32 A, B, C, ..., N.

    Returns:
        N × ... × C × B × A
    """
    rv = args[-1]
    rest = list(reversed(args[:-1]))
    for r in rest:
        rv = dot(rv, r)
    return rv


def rotx(angle):
    """
    Calculate the transform for rotation around the X-axis.

    Arguments:
        angle: Rotation angle in degrees.

    Returns:
        A 4x4 matrix representing a homogeneous coordinates rotation around the X axis.
    """
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    return [[1.0, 0.0, 0.0, 0.0], [0.0, c, -s, 0.0], [0.0, s, c, 0.0], [0.0, 0.0, 0.0, 1.0]]


def roty(ang):
    """
    Calculate the transform for rotation around the Y-axis.

    Arguments:
        angle: Rotation angle in degrees.

    Returns:
        A 4x4 matrix representing a homogeneous coordinates rotation around the Y axis.
    """
    rad = math.radians(ang)
    c = math.cos(rad)
    s = math.sin(rad)
    return [[c, 0.0, s, 0.0], [0.0, 1.0, 0.0, 0.0], [-s, 0.0, c, 0.0], [0.0, 0.0, 0.0, 1.0]]


def rotz(ang):
    """
    Calculate the transform for rotation around the Z-axis.

    Arguments:
        angle: Rotation angle in degrees.

    Returns:
        A 4x4 numpy array of float32 representing a homogeneous coordinates
        matrix for rotation around the Z axis.
    """
    rad = math.radians(ang)
    c = math.cos(rad)
    s = math.sin(rad)
    return [[c, -s, 0.0, 0.0], [s, c, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]


def scale(x=1, y=1, z=1):
    """
    Calculate a scaling matrix.

    Arguments:
        x: Scale factor for x direction (default 1).
        y: Scale factor for y direction (default 1).
        z: Scale factor for z direction (default 1).

    Returns:
        A 4x4 numpy array of float32 representing a homogeneous
        coordinates scaling matrix.
    """
    rv = I()
    rv[0][0], rv[1][1], rv[2][2] = float(x), float(y), float(z)
    return rv


def lookat(eye, center, up):
    """
    Create a viewing matrix.

    Arguments
        eye: 3D point where the viewer is located
        center: 3D point that the eye looks at
        up: 3D upward direction

    Returns:
        A 4x4 numpy array of float32 representing a homogeneous
        coordinates view matrix.
    """
    f = vo.normalize([i-j for i, j in zip(center, eye)])
    s = vo.normalize(vo.cross(f, up))
    u = vo.cross(s, f)
    rv = [
        [s[0], s[1], s[2], -eye[0]],
        [u[0], u[1], u[2], -eye[1]],
        [-f[0], -f[1], -f[2], -eye[2]],
        [0, 0, 0, 1]
    ]
    return rv


def ortho(xyscale):
    """
    Create a simple orthographic projection matrix.

    Arguments:
        xyscale: scaling factor for x and y

    Returns:
        A 4x4 numpy array of float32 representing a homogeneous
        coordinates orthographic projection matrix.
    """
    rv = I()
    rv[0, 0], rv[1, 1] = xyscale, xyscale
    rv[2, 2] = 0
    return rv


def perspective(fovy, width, height, near, far):
    """
    Create a prespective projection matrix.

    Arguments:
        fovy: field of view in y direction, in degrees
        width: width of the viewport
        height: height of the viewport
        znear: near clipping plane (> 0)
        zfar: far clipping plane (> 0)

    Returns:
        A 4x4 numpy array of float32 representing a homogeneous
        coordinates perspective projection matrix.
    """
    aspect = float(width) / float(height)
    f = 1 / math.tan(math.radians(float(fovy)) / 2)
    near = float(near)
    far = float(far)
    d = near - far
    rv = [
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / d, 2 * far * near / d],
        [0, 0, -1, 0]
    ]
    return rv

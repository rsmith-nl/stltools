#!/usr/bin/env python
# vim:fileencoding=utf-8
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2013-07-28 02:07:00 +0200
# Modified: $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to matrix.py. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""3D homogeneous coordinates matrix functions"""

import math
import numpy as np


def I():
    """Returns the 4x4 identity matrix."""
    return np.identity(4, np.float32)


def trans(vec):
    """Returns a 4x4 homogeneous coordinates translation matrix along vec.

    :vec: 3D translation vector
    """
    rv = I()
    rv[0, 3] = vec[0]
    rv[1, 3] = vec[1]
    rv[2, 3] = vec[2]
    return rv


def concat(begin, *rest):
    """Returns the concatenation of the 4x4 matrix arguments.

    :begin, rest: 4x4 matrices
    """
    rv = np.copy(begin)
    for r in rest:
        rv = np.dot(rv, r)
    return rv


def rotx(angle):
    """Returns the 4x4 homogeneous coordinates matrix for rotation around the
    X axis.
    
    :angle: rotation angle in degrees
    """
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([[1.0, 0.0, 0.0, 0.0], 
                     [0.0,   c,  -s, 0.0], 
                     [0.0,   s,   c, 0.0], 
                     [0.0, 0.0, 0.0, 1.0]], np.float32)


def roty(ang):
    """Returns the 4x4 homogeneous coordinates matrix for rotation around the
    Y axis.

    :angle: rotation angle in degrees
    """
    rad = math.radians(ang)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([[  c, 0.0,   s, 0.0],
                     [0.0, 1.0, 0.0, 0.0],
                     [ -s, 0.0,   c, 0.0],
                     [0.0, 0.0, 0.0, 1.0]], np.float32)


def rotz(ang):
    """Returns the 4x4 homogeneous coordinates matrix for rotation around the
    Z axis.

    :angle: rotation angle in degrees
    """
    rad = math.radians(ang)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([[  c,  -s, 0.0, 0.0],
                     [  s,   c, 0.0, 0.0],
                     [0.0, 0.0, 1.0, 0.0],
                     [0.0, 0.0, 0.0, 1.0]]), np.float32


def rot(axis, angle):
    """Returns the 4x4 homogeneous coordinates matrix for rotation around the
    an arbitrary axis by an arbitrary angle.

    :axis: rotation axis
    :angle: rotation angle in degrees
    """
    ax = np.require(axis[0:3], np.float32)
    l = np.linalg.norm(ax)
    if l == 0.0:
        raise ValueError('axis cannot have length 0')
    elif not l == 1.0:
        ax /= l
    ux, uy, uz = ax
    a = math.radians(angle)
    c = math.cos(a)
    s = math.sin(a)
    uc = np.array([[0, -uz, uy], 
                   [uz, 0, -ux], 
                   [-uy, ux, 0]], np.float32)
    ut = np.array([[ux*ux, ux*uy, ux*uz],
                   [ux*uy, uy*uy, uy*uz],
                   [ux*uz, uy*uz, uz*uz]], np.float32)
    m = np.identity(3, np.float32)*c + uc*s + ut*(1.0 - c)
    m = np.vstack((m, np.array([0, 0, 0], np.float32)))
    m = np.column_stack((m, np.array([0, 0, 0, 1], np.float32)))
    return m

#def rotpart(mat):
#    """Return the 3x3 rotation submatrix of a 4x4 matrix
#
#    :mat: 4x4 homogeneous coordinates matrix
#    :returns: 3x3 rotation matrix
#    """
#    return mat[0:3, 0:3]


def lookat(eye, center, up):
    """Create a viewing matrix

    :eye: 3D point where the viewer is located
    :center: 3D point that the eye looks at
    :up: 3D upward direction
    :returns: view matrix
    """
    eye = np.array(eye, np.float32)
    center = np.array(center, np.float32)
    up = np.array(up, np.float32)
    F = center - eye
    f = F/np.linalg.norm(F)
    S = np.cross(f, up)
    s = S/np.linalg.norm(S)
    u = np.cross(s, f)
    rv = np.array([[ s[0],  s[1],  s[2], -eye[0]],
                   [ u[0],  u[1],  u[2], -eye[1]],
                   [-f[0], -f[1], -f[2], -eye[2]],
                   [    0,     0,     0,       1]], np.float32)
    return rv


def perspective(fovy, w, h, znear, zfar):
    """Create a prespective projection matrix.

    :fovy: field of view in y direction, in degrees
    :w: width
    :h: height
    :znear: near clipping plane
    :zfar: far clipping plane
    :returns: projection matrix
    """
    aspect = float(w)/float(h)
    f = 1/math.tan(math.radians(float(fovy))/2)
    znear = float(znear)
    zfar = float(zfar)
    d = znear - zfar
    rv = np.array([[f/aspect, 0, 0, 0],
                   [0, f, 0, 0],
                   [0, 0, (zfar+znear)/d, 2*zfar*znear/d],
                   [0, 0, -1, 0]], np.float32)
    return rv


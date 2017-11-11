# file: stl.py
# vim:fileencoding=utf-8
#
# Copyright © 2013-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2012-11-10 07:55:54 +0100
# Last modified: 2017-06-04 16:40:54 +0200
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
"""Handling STL files and brep datasets."""

import struct
import mmap
from . import vecops as vo
import numpy as np

__version__ = '5.0'


def readstl(name):
    """
    Read an STL file, return the vertices and the name.

    The normal vector information is *discarded* since it is often unreliable.
    Instead the normal vector is calculated from the sequence of the vertices.

    Arguments:
        name: Path of the STL file to read.

    Returns:
        A numpy array of the shape (N, 3) containing the vertices of the
        facets, and the name of the object as given in the STL file.
    """
    with open(name, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        vertices, name = _parsebinary(mm)
        if vertices is None:
            mm.seek(0)
            vertices, name = _parsetxt(mm)
        mm.close()
    if vertices is None:
        raise ValueError('not a valid STL file.')
    return vertices, name


def toindexed(vertices):
    """
    Convert vertices to index format.

    Create an array of unique vertices and an array of indices into the unique
    vertax array that matches the original array.

    Arguments:
        vertices: (?, 3) array of vertex coordinates.

    Returns:
        An (?, 3) array of facet indices and an (M, 3) array of unique points.
    """
    ix, points = vo.indexate(vertices)
    facets = ix.reshape((-1, 3))
    return facets, points


def normals(facets, points):
    """
    Calculate normal vectors of facets.

    Arguments:
        facets: An (?, 3) array of facet indices into points.
        points: An (?, 3) array of unique points.

    Returns:
        an array of normal vector indices for each facet and an array of
        unique normals.
    """
    nv = [vo.normal(points[i], points[j], points[k]) for i, j, k in facets]
    return vo.indexate(nv)


def text(name, ifacets, points, inormals, vectors):
    """
    Make an STL text representation of a brep.

    Arguments:
        name: The name of the object.
        ifacets: A (?, 3) array of indices into the points.
        points: An (?, 3) array of vertex coordinates.
        inormals: An array of indices into the vectors list.
        vectors: An (?, 3) array of normal vectors.

    Returns:
        A string containing a text representation of the brep.
    """
    fcts = list(zip(ifacets, inormals))
    ln = ['solid {}'.format(name)]
    for f, n in fcts:
        ln.append('  facet normal ' + str(vectors[n])[1:-1])
        ln.append('    outer loop')
        for v in f:
            ln.append('      vertex ' + str(points[v])[1:-1])
        ln.append('    endloop')
        ln.append('  endfacet')
    ln.append('endsolid')
    return '\n'.join(ln)


def binary(name, ifacets, points, inormals, vectors):
    """
    Make an STL binary representation of a brep.

    Arguments:
        name: The name of the object.
        ifacets: A (?, 3) array of indices into the points.
        points: An (?, 3) array of vertex coordinates.
        inormals: An array of indices into the vectors list.
        vectors: An (?, 3) array of normal vectors.

    Returns:
        A string containing a binary representation of the brep.
    """
    rc = [struct.pack('<80sI', name.encode('utf-8'), len(ifacets))]
    for fi, ni in zip(ifacets, inormals):
        data = list(
            np.concatenate((vectors[ni], points[fi[0]], points[fi[1]],
                            points[fi[2]]))) + [0]
        rc.append(struct.pack('<12fH', *data))
    return b''.join(rc)


def _striplines(m):
    """
    Generate stripped lines from a memmapped text file.

    Arguments:
        m: A memory mapped file.

    Yields:
        The stripped lines of the file as text.
    """
    while True:
        v = m.readline().decode('utf-8')
        if v:
            yield v.strip()
        else:
            break


def _parsetxt(m):
    """
    Parse a text STL file.

    Arguments:
        m: A memory mapped file.

    Returns:
        The vertices as a (?, 3) numpy array, and the name of the object from
        the file.
    """
    first = m.readline().decode('utf-8')
    name = None
    points = None
    if (first.startswith('solid') and b'facet normal' in m.readline()):
        try:
            name = first.strip().split(None, 1)[1]
        except IndexError:
            name = ''
        vlines = [l.split() for l in _striplines(m) if l.startswith('vertex')]
        points = np.array([tuple(float(k) for k in j[1:])
                           for j in vlines], np.float32)
    m.seek(0)
    return points, name


def _getbp(m):
    """
    Generate points from a binary STL file.

    Arguments:
        m: A memory mapped file.

    Yields:
        The vertices as 3-tuple of floats.
    """
    while True:
        v = m.read(50)
        if len(v) != 50:
            break
        p = struct.unpack('<12x9f2x', v)
        yield tuple(p[0:3])
        yield tuple(p[3:6])
        yield tuple(p[6:])


def _parsebinary(m):
    """
    Parse a binary STL file.

    Arguments:
        m: A memory mapped file.

    Returns:
        The vertices as a list of 3-tuples, and the name of the object from
        the file.
    """
    data = m.read(84)
    name = ''
    points = None
    if b'facet normal' in data:
        return None, None
    name, _ = struct.unpack("<80sI", data[0:84])
    name = name.decode('utf-8')
    name = name.replace("solid ", "")
    name = name.strip('\x00 \t\n\r')
    points = [p for p in _getbp(m)]
    return np.array(points, np.float32), name


def _test(args):
    """
    Test function.

    Arguments:
        args: filename arguments for the test function
    """
    if len(args) < 2:
        print('usage: python stl.py filename')
        exit(1)
    v, nm = readstl(args[1])
    f, p = toindexed(v)
    n, nv = normals(f, p)
    print('Filename: "{}"'.format(args[1]))
    print('Object name: "{}"'.format(nm))
    print('Number of facets:', len(f))
    print('Facet data:')
    for j, k in zip(f, n):
        print(' vertices:', p[j[0]], p[j[1]], p[j[2]])
        print(' normal:', nv[k])


if __name__ == '__main__':
    from sys import argv
    _test(argv)

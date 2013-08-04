# # -*- coding: utf-8 -*-
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

# Check this code with 'pylint -r n stl.py'

"""Handling STL files and brep datasets."""

from __future__ import print_function, division
import struct
import mmap
import vecops as vo
import numpy as np


__version__ = '$Revision$'[11:-2]


def _striplines(m):
    """Generator to yield stripped lines from a memmapped text file.

    :m: A memory mapped file.
    :yields: The stripped lines of the file, one at a time.
    """
    while True:
        v = m.readline()
        if v:
            yield v.strip()
        else:
            break


def _parsetxt(m):
    """Parses the file if it is an text STL file.

    :m: A memory mapped file.
    :returns: The vertices as a list of 3-tuples, and the name of the 
    object from the file.
    """
    first = m.readline()
    name = None
    points = None
    if (first.startswith('solid') and
        'facet normal' in m.readline()):
        try:
            name = first.strip().split(None, 1)[1]
        except IndexError:
            name = ''
        vlines = [l.split() for l in _striplines(m) if l.startswith('vertex')]
        points = np.array([tuple(float(k) for k in j[1:]) for j in vlines],
                          np.float32)
    m.seek(0)
    return points, name


def _getbp(m):
    """Generator to yield points from a binary STL file.

    :m: A memory mapped file.
    :yields: The vertices as 3-tuple of floats.
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
    """Parses the file if it is a binary STL file.

    :m: A memory mapped file.
    :returns: The vertices as a list of 3-tuples, and the name of the object
    from the file.
    """
    data = m.read(84)
    name = ''
    points = None
    if 'facet normal' in data:
        return None, None
    name, _ = struct.unpack("<80sI", data[0:84])
    name = name.replace("solid ", "")
    name = name.strip('\x00 \t\n\r')
    points = [p for p in _getbp(m)] 
    return np.array(points, np.float32), name


def readstl(name):
    """Reads an STL file, returns the vertices and the name. 
    The normal vector information is discarded since it is often unreliable.

    :name: path of the STL file to read
    :returns: a numpy array of the shape (N, 3) containing the vertices 
    of the facets, and the name of the object as given in the STL file.
    """
    with open(name, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        vertices, name = _parsebinary(mm)
        if vertices == None:
            mm.seek(0)
            vertices, name = _parsetxt(mm)
        mm.close()
    if vertices == None:
        raise ValueError('not a valid STL file.')
    #ix, points = vecops.indexate(points)
    #facets = zip(ix[::3], ix[1::3], ix[2::3])
    return vertices, name


def toindexed(vertices):
    """Convert a numpy array of vertices of an indexed array facets and 
    an array of unique vertices.

    :vertices: (N, 3) array of vertex coordinates
    :returns: an (N, 3) array of facet indices and an (M, 3) array of 
    unique points.
    """
    ix, points = vo.indexate(vertices)
    facets = ix.reshape((-1, 3))
    return facets, points


def normals(facets, points):
    """Calculate normal vectors of facets

    :facets: an (N, 3) array of facet indices into points
    :points: an (M, 3) array of unique points
    :returns: an array of normal vector indices for each
    facet and an array of unique normals
    """
    nv = [vo.normal(points[i], points[j], points[k])
          for i, j, k in facets]
    return vo.indexate(nv)


def text(name, ifacets, points, inormals, vectors):
    """Make an STL text representation of a brep.

    :name: A string containing the name of the object.
    :ifacets: List of indices into the points list.
    :points: List of point coordinates.
    :inormals: List of indices into the vectors list.
    :vectors: List of normal vectors
    :returns: A string containing a text representation of the brep.
    """
    fcts = zip(ifacets, inormals)
    ln = ['solid {}'.format(name)]
    for f, n in fcts:
        ln.append('  facet normal ' + str(vectors[n])[2:-1])
        ln.append('    outer loop')
        for v in f:
            ln.append('      vertex ' + str(points[v])[2:-1])
        ln.append('    endloop')
        ln.append('  endfacet')
    ln.append('endsolid')
    return '\n'.join(ln)


def binary(name, ifacets, points, inormals, vectors):
    """Make an STL binary representation of a brep.

    :name: A string containing the name of the object.
    :ifacets: List of indices into the points list.
    :points: List of point coordinates.
    :inormals: List of indices into the vectors list.
    :vectors: List of normal vectors
    :returns: A string containing a binary representation of the brep.
    """
    rc = [struct.pack('<80sI', name, len(ifacets))]
    for fi, ni in zip(ifacets, inormals):
        a, b, c, n = points[fi[0]], points[fi[1]], points[fi[2]], vectors[ni]
        data = n + a + b + c + (0,)
        rc.append(struct.pack('<12fH', *data))
    return ''.join(rc)


def _test(args):
    """Test function

    :args: filename arguments for the test function
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

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

__version__ = '$Revision$'[11:-2]

import struct
import mmap
import vecops

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
        name = first.strip().split(None, 1)[1]
        vlines = [l.split() for l in _striplines(m) if l.startswith('vertex')]
        points = [tuple(float(k) for k in j[1:]) for j in vlines]
    m.seek(0)
    return points, name


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


def _parsebinary(m):
    """Parses the file if it is a binary STL file.

    :m: A memory mapped file.
    :returns: The vertices as a list of 3-tuples, and the name of the object
    from the file.
    """
    data = m.read(84)
    name = None
    points = None
    if not 'facet normal' in data:
        name, _ = struct.unpack("=80sI", data[0:84])
        name = name.replace("solid ", "")
        name = name.strip('\x00 \t\n\r')
        points = [p for p in _getbp(m)] 
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
        p = struct.unpack('=12x9f2x', v)
        yield tuple(p[0:3])
        yield tuple(p[3:6])
        yield tuple(p[6:])


def readstl(name):
    """Reads an STL file

    :name: Path of the STL file to read.
    :returns: A tuple (facets, points, name). Where facets is a list of
    3-tuples which contain indices into the points list. Points is a list of
    3-tuples containing the vertex coordinates. Name is the name of the object
    given in the STL file.
    """
    with open(name, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        points, name = _parsebinary(mm)
        if not points:
            mm.seek(0)
            points, name = _parsetxt(mm)
        mm.close()
    if not points:
        raise ValueError('not a valid STL file.')
    ix, points = vecops.indexate(points)
    facets = zip(ix[::3], ix[1::3], ix[2::3])
    return facets, points, name


def normals(facets, points):
    """Calculate normal vectors of facets

    :facets: List of facets. Each facet is a 3-tuple of indices in points
    :points: List of points.
    :returns: A tuple containing a list of normal vector indices for each
    facet and a list of unique normals.
    """
    nv = [vecops.normal(points[i], points[j], points[k])
          for i, j, k in facets]
    return vecops.indexate(nv)


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
        ln.append('  facet normal ' + vecops.mkstr(vectors[n], sep=' '))
        ln.append('    outer loop')
        for v in f:
            ln.append('      vertex ' + vecops.mkstr(points[v], sep=' '))
        ln.append('    endloop')
        ln.append('  endfacet')
    ln.append('endsolid')
    return '\n'.join(ln)


def _test(args):
    """Test function

    :args: filename arguments for the test function
    """
    if len(args) < 1:
        print('usage: python stlfile.py filename')
    f, p, nm = readstl(argv[1])
    n, nv = normals(f, p)
    print 'Filename: "{}"'.format(args[0])
    print 'Object name: "{}"'.format(nm)
    print 'Number of facets:', len(f)
    print 'Facet data:'
    for j, k in zip(f, n):
        print ' vertices:', p[j[0]], p[j[1]], p[j[2]]
        print ' normal:', nv[k]

if __name__ == '__main__':
    from sys import argv
    _test(argv[1:])

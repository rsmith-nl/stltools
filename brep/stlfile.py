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

# Check this code with 'pylint -r n vector.py'

"""Reading an STL file."""

__version__ = '$Revision$'[11:-2]

import struct
import mmap


def _parsetxt(m):
    """Parses the file if it is an text STL file.

    :m: memory mapped file
    :returns: the vertices as a list of 3-tuples, and the name of the object.
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

    :m: memory mapped file
    :yields: the stripped lines of the file
    """
    while True:
        v = m.readline()
        if v:
            yield v.strip()
        else:
            break


def _parsebinary(m):
    """Parses the file if it is a binary STL file.

    :m: memory mapped file
    :returns: the vertices as a list of 3-tuples, and the name of the object.
    """
    data = m.read(84)
    m.seek(0)
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

    :m: memory mapped file
    :yields: the vertices as 3-tuple of floats
    """
    while True:
        v = m.read(50)
        if len(v) != 50:
            break
        p = struct.unpack('=12x9f2x', v)
        yield tuple(p[0:2])
        yield tuple(p[3:5])
        yield tuple(p[6:])


def readstl(name):
    """Reads an STL file

    :name: path of the STL file to read
    :returns: (facets, points, name) Where facets is a list of 3-tuples
    which contain indices into the points list. Points is a list of 3-tuples
    containing the vertex coordinates. Name is the name of the object given in
    the STL fil
    """
    with open(name, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        points, name = _parsebinary(mm)
        if not points:
            points, name = _parsetxt(mm)
        mm.close()
    if not points:
        raise ValueError('not a valid STL file.')
    vd = {}
    ix = [vd.setdefault(p, len(vd)) for p in points]
    facets = zip(ix[::3], ix[1::3], ix[2::3])
    vm = sorted([(v, k) for k, v in vd.iteritems()], key=lambda x: x[0])
    points = [i[1] for i in vm]
    return facets, points, name

def _test(args):
    """Test function

    :args: filename arguments for the test function
    """
    if len(args) < 1:
        print('usage: python stlfile.py filename')
    f, p, nm = readstl(argv[1])
    print 'Filename: "{}"'.format(args[0])
    print 'Object name: "{}"'.format(nm)
    print 'Number of facets:', len(f)
    print 'Facet data:'
    for j in f:
        print ' ', p[j[0]], p[j[1]], p[j[2]]

if __name__ == '__main__':
    from sys import argv
    _test(argv[1:])

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

from os.path import basename
import struct
import mmap

def _istxt(mm):
    first = mm.readline()
    name = None
    points = None
    if (first.startswith('solid') and
        'facet normal' in mm.readline()):
        name = first.strip().split(maxsplit=1)[1]
        vlines = [l.split() for l in _striplines(mm) if l.startswith('vertex')]
        points = [tuple(float(k) for k in j[1:]) for j in vlines]
    mm.seek(0)
    return points, name


def _isbinary(mm):
    data = mm.read(84)
    mm.seek(0)
    name = None
    points = None
    if not 'facet normal' in data:
        name, _ = struct.unpack("=80sI", data[0:84])
        name = name.replace("solid ", "")
        name = name.strip('\x00 \t\n\r')
        points = [p for p in _getbp(mm)] 
    return points, name


def _striplines(m):
    while True:
        v = m.readline()
        if v:
            yield v.strip()
        else:
            break


def _getbp(m):
    while True:
        v = m.read(50)
        if v:
            p = struct.unpack('=12x9f2x', v)
            yield tuple(p[0:2])
            yield tuple(p[3:5])
            yield tuple(p[6:])
        else:
            break


def readfile(name):
    with open(name, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        points, name = _isbinary(mm)
        if not points:
            points, name = _istxt(mm)
        mm.close()
    if not points:
        raise ValueError('not a valid STL file.')
    vd = {}
    ix = [vd.setdefault(p, len(vd)) for p in points]
    ix = zip(ix[::3], ix[1::3], ix[2::3])
    vm = sorted([(v, k) for k, v in vd.iteritems()], key=lambda x: x[0])
    sp = [i[1] for i in vm]
    return ix, sp, name


class StlReader(object):
    """Object for reading STL files."""
    __slots__ = ['_fname', '_n', '_type', 'name', '_reader']

    @staticmethod
    def _readbinary(items):
        """Process the contents of a binary STL file as a
        generator.

        :items: file data minus header split into 50-byte blocks.
        :yields: a 3-tuple of Vectors
        """
        # Process the items
        for i in items:
            f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
            struct.unpack("=12x9f2x", i)
            a = (f1x, f1y, f1z)
            b = (f2x, f2y, f2z)
            c = (f3x, f3y, f3z)
            yield (a, b, c)

    @staticmethod
    def _readtext(items):
        """Process the contents of a text STL file as a
        generator.

        :items: stripped lines of the text STL file
        :yields: a 3-tuple of Vectors
        """
        # Items now begins with "facet"
        while items[0] == "facet":
            a = (float(items[8]), float(items[9]), float(items[10])) 
            b = (float(items[12]), float(items[13]), float(items[14]))
            c = (float(items[16]), float(items[17]), float(items[18]))
            del items[:21]
            yield (a, b, c)

    def __init__(self, name):
        """Reads the named STL file into memory for processing.

        :name: name of the file to open
        """
        self._fname = name
        with open(name, 'r') as sf:
            data = sf.read()
        if data.find('vertex', 120) == -1: # Binary file format
            self._type = 'binary'
            name, nf1 = struct.unpack("=80sI", data[0:84])
            name = name.replace("solid ", "")
            name = name.strip('\x00 \t\n\r')
            if len(name) == 0:
                self.name = basename(name)[:-4]
            else:
                self.name = name
            data = data[84:]
            facetsz = len(data)
            nf2 = int(facetsz/50)
            if nf1 != nf2:
                t = "Number of facets doesn't match file size."
                raise ValueError(t)
            items = [data[n:n+50] for n in range(0, facetsz, 50)]
            self._n = nf2
            self._reader = StlReader._readbinary(items)
        else: # text format
            self._type = 'text'
            items = [s.strip() for s in data.split()]
            try:
                sn = items.index("solid")+1
                en = items.index("facet")
            except:
                raise ValueError("Not an STL file.")
            if sn == en:
                self.name = 'unknown'
            else:
                self.name = ' '.join(items[sn:en])
            nf1 = items.count('facet')
            del items[0:en]
            self._n = nf1
            self._reader = StlReader._readtext(items)

    @property
    def filename(self):
        """Returns the name of the STL file."""
        return self._fname

    @property
    def numfacets(self):
        """Returns the number of facets in the STL file."""
        return self._n

    @property
    def filetype(self):
        """Returns the type of the STL file."""
        return self._type

    def __iter__(self):
        """Iterates over the facets from the STL file.
        Every iteration yields a 3-tuple of 3-tuples of floats
        """
        return self._reader

    def readall(self):
        """Read all facets and return them in a list of Vector3 3-tuples.
        """
        return [f for f in self._reader]

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2:
        print('usage: python', argv[0], 'filename')
        exit(1)
    r = StlReader(argv[1])
    print 'Filename', r.filename
    print 'Type:', r.filetype
    print 'Number of facets:', r.numfacets
    print 'Facet data:'
    for va, vb, vc in r:
        print '  ', va, vb, vc


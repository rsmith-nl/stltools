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

# Check this code with 'pylint -r n read.py'

"""Reading triangulated models."""

__version__ = '$Revision$'[11:-2]

import struct
from os.path import basename
from . import vector

class Facets(object):

    def __init__(self, name):
        self.name = name
        self.facets = []
        self.minx = None
        self.maxx = None
        self.miny = None
        self.maxy = None
        self.minz = None
        self.maxz = None

    def addfacet(self, f):
        a, b, c = f
        u = vector.sub(b, a)
        v = vector.sub(c, b)
        n = vector.cross(u, v)
        try:
            n  = vector.norm(n)
        except ValueError:
            n = None
        self.facets.append((a, b, c, n))

    def stats(self, prefix=''):
        if not self.minx:
            points = [f[0] for f in self.facets]
            points += [f[1] for f in self.facets]
            points += [f[2] for f in self.facets]
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            z = [p[2] for p in points]
            self.minx = min(x)
            self.maxx = max(x)
            self.miny = min(y)
            self.maxy = max(y)
            self.minz = min(z)
            self.maxz = max(z)
        outs = prefix + 'Model name: "{}"\n'.format(self.name)
        outs += prefix + '{} facets\n'.format(len(self.facets))
        outs += prefix + "3D Extents of the model (in STL units):\n"
        outs += prefix + "{} ≤ x ≤ {},\n".format(self.minx, self.maxx)
        outs += prefix + "{} ≤ y ≤ {},\n".format(self.miny, self.maxy)
        outs += prefix + "{} ≤ z ≤ {}.\n".format(self.minz, self.maxz)
        s = "3D center (midpoint of extents, STL units): <{0}, {1}, {2}>.\n"
        outs += prefix + s.format((self.minx + self.maxx)/2.0, 
                                  (self.miny + self.maxy)/2.0, 
                                  (self.minz +self. maxz)/2.0)
        s = "3D mean (mean of all vertices, STL units): <{0}, {1}, {2}>."
        x, y, z = vector.mean(points)
        outs += prefix + s.format(x, y, z)
        return outs


class Surface(object):

    def __init__(self, name):
        self.name = name
        self.points = []
        self.normals = []
        self.ilines = []
        self.ifacets = []
        self.xmin = self.xmax = None
        self.ymin = self.ymax = None
        self.zmin = self.zmax = None

    def __len__(self):
        return len(self.ifacets)

    def _extents(self):
        x = [p[0] for p in self.points]
        y = [p[1] for p in self.points]
        z = [p[2] for p in self.points]
        self.xmin = min(x)
        self.xmax = max(x)
        self.ymin = min(y)
        self.ymax = max(y)
        self.zmin = min(z)
        self.zmax = max(z)

    def addfacet(self, f):
        a, b, c, n = f
        if n == None:
            return # Skip degenerate facets.
        stat = ''
        # Normal vector
        try:
            newni = self.normals.index(n)
        except ValueError:
            newni = len(self.normals)
            self.normals.append(f[3])
            stat += 'Found 1 new normal, index {}. '.format(newni)
        # Vertices:
        newpi = []
        nnp = []
        for x in a, b, c:
            try:
                newpi.append(self.points.index(x))
            except ValueError:
                i = len(self.points)
                newpi.append(i)
                self.points.append(x)
                nnp.append(i)
        if nnp:
            stat += 'Found {} new points; {}. '.format(len(nnp), str(nnp))
        # Lines
        newpi.sort()
        lines = [(newpi[0], newpi[1]), (newpi[1], newpi[2]), 
                    (newpi[2], newpi[0])]
        newli = []
        nni = []
        for l in lines:
            try:
                newli.append(self.ilines.index(l))
            except ValueError:
                i = len(self.ilines)
                newli.append(i)
                self.ilines.append(l)
                nni.append(i)
        if nni:
            stat += 'Found {} new lines; {}.'.format(len(nni), str(nni))
        # Facet
        self.ifacets.append((tuple(newpi), newni, tuple(newli)))
        return stat

    def __str__(self):
        outs = "solid {}\n".format(self.name)
        for (v, n, l) in self.ifacts:
            nv = self.normal[n]
            outs +=  '  facet normal {} {} {}\n'.format(nv[0], nv[1], nv[2])
            outs += '    outer loop\n'
            for i in v:
                p = self.points[i]
                outs += '      vertex {} {} {}\n'.format(p[0], p[1], p[2])
            outs += '    endloop\n  endfacet\n'
        outs +='endsolid\n'
        return outs

    def stats(self, prefix=''):
        """Return statistics about an STL model.
        """
        if self.xmin == None:
            x = [p[0] for p in self.points]
            y = [p[1] for p in self.points]
            z = [p[2] for p in self.points]
            self.xmin = min(x)
            self.xmax = max(x)
            self.ymin = min(y)
            self.ymax = max(y)
            self.zmin = min(z)
            self.zmax = max(z)
        s = prefix + 'Model name: "{}"\n'.format(self.name)
        s = prefix + "{} facets, {} vertices, {} normal vectors, {} edges.\n"
        outs = s.format(len(self.ifacets), len(self.points), 
                        len(self.normals), len(self.ilines))
        outs += prefix + "3D Extents of the model (in STL units):\n"
        outs += prefix + "{} ≤ x ≤ {},\n".format(self.xmin, self.xmax)
        outs += prefix + "{} ≤ y ≤ {},\n".format(self.ymin, self.ymax)
        outs += prefix + "{} ≤ z ≤ {}.\n".format(self.zmin, self.zmax)
        s = "3D center (midpoint of extents, STL units): <{0}, {1}, {2}>.\n"
        outs += prefix + s.format((self.xmin + self.xmax)/2.0, 
                                  (self.ymin + self.ymax)/2.0, 
                                  (self.zmin + self.zmax)/2.0)
        s = "3D mean (mean of all vertices, STL units): <{0}, {1}, {2}>."
        x, y, z = vector.mean(self.points)
        outs += prefix + s.format(x, y, z)
        return outs


def fromfile(fname):
    """Read an STL file.
    
    Arguments:
    fname -- file to read the STL file from.

    Returns:
    facets -- a Facets object.
    """
    def _readbinary(items=None):
        """Process the contents of a binary STL file as a
        generator.

        Arguments:
        items -- file data minus header split into 50-byte blocks.

        Yields:
        a RawFacet
        """
        # Process the items
        for cnt, i in enumerate(items):
            f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
            struct.unpack("=12x9f2x", i)
            a = (f1x, f1y, f1z)
            b = (f2x, f2y, f2z)
            c = (f3x, f3y, f3z)
            yield (a, b, c)

    def _readtext(items=None):
        """Process the contents of a text STL file as a
        generator.

        Arguments:
        items -- stripped lines of the text STL file

        Yields:
        a RawFacet
        """
        # Items now begins with "facet"
        while items[0] == "facet":
            a = (float(items[8]), float(items[9]), float(items[10]))
            b = (float(items[12]), float(items[13]), float(items[14]))
            c = (float(items[16]), float(items[17]), float(items[18]))
            del items[:21]
            yield (a, b, c)

    with open(fname, 'r') as stlfile:
        data = stlfile.read()
    if data.find('vertex', 120) == -1: # Binary file format
        name, nf1 = struct.unpack("=80sI", data[0:84])
        name = name.replace("solid ", "")
        name = name.strip('\x00 \t\n\r')
        if len(name) == 0:
            name = basename(fname)[:-4]
        data = data[84:]
        facetsz = len(data)
        nf2 = facetsz / 50
        if nf1 != nf2:
            raise ValueError("Number of facets doesn't match file size.")
        items = [data[n:n+50] for n in range(0, facetsz, 50)]
        reader = _readbinary(items)
    else: # Text file format
        items = [s.strip() for s in data.split()]
        try:
            sn = items.index("solid")+1
            en = items.index("facet")
        except:
            raise ValueError("Not an STL file.")
        if sn == en:
            name = 'unknown'
        else:
            name = ' '.join(items[sn:en])
        nf1 = items.count('facet')
        del items[0:en]
        reader = _readtext(items)
    fl = Facets(name)
    for f in reader:
        fl.addfacet(f)
    return fl




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

# Check this code with 'pylint -r n xtrude.py'

"""Create extruded brep models."""

__version__ = '$Revision$'[11:-2]

from .stl import IndexedMesh

class Sketch(object):

    def __init__(self, name):
        self.name = name
        self.items = []
        self.ip = None
        self.cp = None
        self.closed = False

    def _chk(self):
        if self.closed:
            raise ValueError('sketch is closed')
        if not self.cp:
            raise ValueError('no currentpoint set')

    def moveto(self, x=0, y=0):
        if self.closed:
            raise ValueError('sketch is closed')
        if self.items:
            raise ValueError('sketch has already been started')
        self.ip = self.cp = (float(x), float(y))

    def lineto(self, x, y):
        self._chk()
        newpoint = (float(x), float(y))
        line = (self.cp, newpoint)
        self.items.append(line)
        self.cp = newpoint

    def rlineto(self, dx, dy):
        self._chk()
        x = self.cp[0] + float(dx)
        y = self.cp[1] + float(dy)
        self.lineto(x, y)

    def arc(self, x, y, r, ang1, ang2):
        self._chk()
        pass

    def curveto(self, x1, y1, x2, y2, x3, y3):
        self._chk()
        pass

    def closepath(self):
        if self.ip != self.cp:
            self.lineto(self.ip[0], self.ip[1])
        self.closed = True

    def erase(self):
        self.__init__(self.name)

    def extrude(self, dx, dy, xz):
        pass

# file: utils.py
# vim:fileencoding=utf-8
#
# Copyright © 2013-2015 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2013-07-07 21:01:52  +0200
# Last modified: 2017-08-22 17:02:04 +0200
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
"""Utilities for stltools."""

import argparse
import os.path
import re

__version__ = '5.0'


class RotateAction(argparse.Action):
    """Gather rotation options."""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Create RotateAction object."""
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(RotateAction, self).__init__(option_strings, dest,
                                           **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Implement rotate option."""
        rotations = getattr(namespace, 'rotations', None)
        if not rotations:
            rotations = []
        rotations += [(option_string[1], values)]
        setattr(namespace, 'rotations', rotations)


def outname(inname, extension, addenum=''):
    """
    Create the name of the output filename based on the input filename.

    Arguments:
        inname: Name + path of the input file.
        extension: Extension of the output file.
        addenum: String to append to filename.

    Returns:
        Output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    rv = re.sub('^[\s\.]+|\s+$', '', rv)
    rv = re.sub('\s+', '_', rv)
    if not extension.startswith('.'):
        extension = '.' + extension
    return rv + addenum + extension


def num2rgb(color):
    """Convert a color value into r,b,g colors in the range 0−1.

    The input is an integer that is clamped to the range 0−0xFFFFFF.
    This is then separated in red, green and blue components.

    Arguments:
        color: integer color value.

    Returns:
        (r, g, b) tuple where each component is in the range 0−1.
    """
    if color > 0xFFFFFF:
        color = 0xFFFFFF
    elif color < 0:
        color = 0
    red = ((color & 0xFF0000) >> 16)/255
    green = ((color & 0x00FF00) >> 8)/255
    blue = (color & 0x0000FF)/255
    return red, green, blue

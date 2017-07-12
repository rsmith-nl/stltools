# file: utils.py
# vim:fileencoding=utf-8
#
# Copyright © 2013,2014 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Created: 2013-07-07 21:01:52  +0200
# $Date$
# $Revision$
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

from __future__ import print_function, division
import os.path
from datetime import datetime
import glob
import sys
import matrix as m

__version__ = '3.3'


def outname(inname, extension, addenum=''):
    """Creates the name of the output filename based on the input filename.

    :inname: name + path of the input file
    :extension: extension of the output file.
    :addenum: string to append to filename
    :returns: output file name.
    """
    rv = os.path.splitext(os.path.basename(inname))[0]
    if rv.startswith('.') or rv.isspace():
        raise ValueError("Invalid file name!")
    if not extension.startswith('.'):
        extension = '.' + extension
    return rv + addenum + extension


def skip(error, filename):
    """Skip a file in case of an error

    :error: exception
    :filename: name of file to skip
    """
    print("Cannot read file: {}".format(error))
    print("Skipping file '{}'".format(filename))


def hex2rgb(hex):
    """Convert hex color code to rgb(ish) for cairo"""
    hex_length = len(hex)
    if hex_length == 6:
        r = float(int(hex[0:2], 16)) / 255
        g = float(int(hex[2:4], 16)) / 255
        b = float(int(hex[4:6], 16)) / 255
    else:
        r = 1
        g = 1
        b = 1
    return r, g, b


def processargs(args, ext, use):
    """Process the command-line arguments for a program that does coordinate
    transformations.

    :args: The command line arguments without the program name.
    :ext: The extension of the output file.
    :use: A function for printing a usage message.
    :returns: A tuple containing the input file name, the output filename and
    the transformation matrix.
    """
    transformargs = ['x', 'y', 'z', 'X', 'Y', 'Z']
    if len(args) < 1:
        use()
        sys.exit(0)
    else:
        infile = ''
        outfile = None
        tr = m.I()
        infile = args[0]
        bg_color = None
        fg_color = None
        del args[0]
        for arg in args:
            if 'stl' in arg:  # Hack
                infile = arg
        for arg in args:
            arg_index = args.index(arg)
            if arg in transformargs:
                try:
                    ang = float(args[arg_index +1])
                    if arg in ['x', 'X']:
                        add = m.rotx(ang)
                    elif arg in ['y', 'Y']:
                        add = m.roty(ang)
                    else:
                        add = m.rotx(ang)
                    tr = m.concat(tr, add)
                except:
                    print("Argument '{}' is not a number, ignored."
                          .format(arg))
                    continue
            elif arg == '--output':
                outfile = args[arg_index + 1]
            elif arg == '--bg':
                bg_color = args[arg_index + 1]
            elif arg == '--fg':
                fg_color = args[arg_index + 1]
    if outfile == None:
        outfile = outname(infile, ext)
    return (infile, outfile, tr, bg_color, fg_color)


def xpand(args):
    """Expand command line arguments for operating systems incapable of doing
    so.

    :args: list of argument
    :returns: expanded argument list
    """
    xa = []
    for a in args:
        xa += glob.glob(a)
    return xa


class Msg(object):
    """Message printer"""

    def __init__(self):
        """@todo: to be defined1 """
        self.start = datetime.now()

    def say(self, *args):
        """@todo: Docstring for message

        :*args: @todo
        :returns: @todo
        """
        delta = datetime.now() - self.start
        print('['+str(delta)[:-4]+']:', *args)

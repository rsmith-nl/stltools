# -*- coding: utf-8 -*-
#
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

"""Utilities for nctools."""

import os.path
import glob
import sys
import matrix as m

__version__ = '$Revision$'[11:-2]


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
    print "Cannot read file: {}".format(error)
    print "Skipping file '{}'".format(filename)


def processargs(args, ext, use):
    """Process the command-line arguments for a program that does coordinate
    transformations.

    :args: The command line arguments without the program name.
    :ext: The extension of the output file.
    :use: A function for printing a usage message.
    :returns: A tuple containing the input file name, the output filename and
    the transformation matrix.
    """
    validargs = ['x', 'y', 'z', 'X', 'Y', 'Z']
    if len(args) < 1:
        use()
        sys.exit(0)
    infile = args[0]
    if len(args) < 2 or args[1] in validargs:
        outfile = None
        del args[:1]
        outfile = outname(infile, ext)
    else:
        outfile = args[1]
        del args[:2]
    tr = m.I()
    while len(args) > 1:
        if not args[0] in validargs:
            print "Unknown argument '{}' ignored.".format(args[0])
            del args[0]
            continue
        try:
            ang = float(args[1])
            if args[0] in ['x','X']:
                add = m.rotx(ang)
            elif args[0] in ['y','Y']:
                add = m.roty(ang)
            else:
                add = m.rotx(ang)
            del args[:2]
            tr = m.concat(add, tr)
        except:
            print "Argument '{}' is not a number, ignored.".format(args[1])
            continue
    return (infile, outfile, tr)


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

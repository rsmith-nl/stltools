#! /usr/bin/env python3
# vim:fileencoding=utf-8
#
# Copyright © 2012-2017 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# Last modified: 2017-08-22 10:39:02 +0200
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
"""Program for converting an STL file into a POV-ray mesh or mesh2."""

import argparse
import base64
import hashlib
import logging
import os
import re
import sys
import time
from stltools import stl, utils

__version__ = '5.0'


def valid_name(name):
    """Check if a name is a valid POV-ray identifier.

    Valid names consist out of letters, numbers and underscore. The POV-ray
    documentation doesn't say explicitly, so we will assume that to mean ASCII.
    The maximum length of identifiers is 40 characters. But since we prepend
    'm_' to the name of the mesh, we will look for a maximum of 38 characters.

    Arguments:
        name: String containing the object name from the STL file.

    Returns:
        True if the name is a valid identifier, otherwise False.
    """
    validfmt = '^[a-zA-Z0-9_]{1,38}$'
    if re.search(validfmt, name):
        return True
    return False


def generate_name(orig_name, path):
    """Generate a valid identifier for a mesh object.

    The valid identifier is based on the object name if that is not an empty
    string. In the latter case, it is based on the name of the STL file.

    The input is hased with SHA1 and then encoded with base32. Eight bytes are
    taken out of that result and converted to lowercase ASCII.


    Arguments:
        orig_name: String containing the object name.
        path: String containing the path to the file.

    Returns:
        A valid identifier.
    """
    base = orig_name
    if len(orig_name) == 0:
        base = os.path.basename(path)
    return base64.b32encode(
        hashlib.sha1(base.encode('utf-8')).digest()
    )[8:16].decode('ascii').lower()


def mesh1(name, vertices):
    """
    Create a POV-ray mesh description from vertices data.

    Arguments:
        name: The name of the object.
        vertices: An (N,3) numpy array containing the vertex data.

    Returns:
        A string representation of a POV-ray mesh object.
    """
    facets = vertices.reshape((-1, 9))
    lines = ["# declare m_{} = mesh {{".format(name.replace(' ', '_'))]
    # The indices sequence 1, 0, 2 is used because of the difference between
    # the STL coordinate system and that used in POV-ray.
    fct = "  triangle {{\n    <{1}, {0}, {2}>,\n    <{4}, {3}, {5}>,\n" \
          "    <{7}, {6}, {8}>\n  }}"
    lines += [fct.format(*f) for f in facets]
    lines += ['}']
    return '\n'.join(lines)


def mesh2(name, vertices):
    """
    Create a POV-ray mesh2 object from facet data.

    Arguments:
        name: The name of the object.
        vertices: An (N,3) numpy array containing the vertex data.

    Returns:
        A string representation of a POV-ray mesh2 object.
    """
    ifacets, points = stl.toindexed(vertices)
    lines = [
        "# declare m_{} = mesh2 {{".format(name), '  vertex_vectors {',
        '    {},'.format(len(points))
    ]
    # The indices sequence 1, 0, 2 is used because of the difference between
    # the STL coordinate system and that used in POV-ray
    lines += ['    <{1}, {0}, {2}>,'.format(*p) for p in points]
    lines[-1] = lines[-1][:-1]
    lines += ['  }\n  face_indices {', '    {},'.format(len(ifacets))]
    lines += ['    <{0}, {1}, {2}>,'.format(*f) for f in ifacets]
    lines[-1] = lines[-1][:-1]
    lines += ['  }', '}']
    return '\n'.join(lines)


def main(argv):
    """
    Entry point for stl2pov.

    Arguments:
        argv: List of command line arguments (without program name!)
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = 'generate a mesh2 object (slow on big files)'
    parser.add_argument(
        '-2,'
        '--mesh2', action='store_true', help=argtxt, dest='mesh2')
    parser.add_argument(
        '-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')")
    parser.add_argument('file', nargs='*', help='one or more file names')
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format='%(levelname)s: %(message)s')
    if not args.file:
        parser.print_help()
        sys.exit(0)
    for fn in args.file:
        logging.info('Starting file "{}"'.format(fn))
        if not fn.lower().endswith('.stl'):
            w = 'the file "{}" is probably not an STL file, skipping'
            logging.warning(w.format(fn))
            continue
        try:
            logging.info('Reading facets')
            vertices, name = stl.readstl(fn)
            outfn = utils.outname(fn, '.inc')
        except Exception as e:  # pylint: disable=W0703
            logging.error('{}: {}'.format(fn, e))
            continue
        if not valid_name(name):
            ws = 'the object name "{}" is not a valid POV-ray identifier.'
            logging.warning(ws.format(name))
            name = generate_name(name, fn)
            logging.warning('using "m_{}" instead.'.format(name))
        outs = "// Generated by stl2pov {}\n".format(__version__)
        outs += "// on {}.\n".format(time.asctime())
        outs += "// Source file name: '{}'\n".format(fn)
        if args.mesh2:
            logging.info('generating mesh2 data.')
            outs += mesh2(name, vertices)
        else:
            logging.info('generating mesh data.')
            outs += mesh1(name, vertices)
        try:
            with open(outfn, 'w+') as of:
                logging.info('writing output file "{}".'.format(outfn))
                of.write(outs)
        except Exception:
            logging.warning('cannot write output file "{}".'.format(outfn))
            continue
        logging.info('done with file "{}".'.format(fn))


if __name__ == '__main__':
    main(sys.argv[1:])

#! /usr/bin/env python3
# file: stl2pov.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2011-2020 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2011-04-10T18:33:02+02:00
# Last modified: 2020-10-04T16:59:23+0200
"""Program for converting an STL file into a POV-ray mesh or mesh2."""

import argparse
import base64
import hashlib
import logging
import os
import re
import sys
import time
from stltools import stl, utils, __version__


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
    validfmt = "^[a-zA-Z0-9_]{1,38}$"
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
    return base64.b32encode(hashlib.sha1(base.encode("utf-8")).digest()
                            )[8:16].decode("ascii").lower()


def mesh1(name, vertices):
    """
    Create a POV-ray mesh description from vertices data.

    Arguments:
        name: The name of the object.
        vertices: An (N,3) numpy array containing the vertex data.

    Returns:
        A string representation of a POV-ray mesh object.
    """
    numbers = [n for p in vertices for n in p]
    facets = utils.chunked(numbers, 9)
    uname = name.replace(' ', '_')
    lines = [f"# declare m_{uname} = mesh {{"]
    # The indices sequence 0, 2, 1 is used because of the difference between
    # the STL coordinate system and that used in POV-ray.
    fct = "  triangle {{\n    <{0}, {2}, {1}>,\n    <{3}, {5}, {4}>,\n" \
          "    <{6}, {8}, {7}>\n  }}"
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
        f"# declare m_{name} = mesh2 {{",
        "  vertex_vectors {",
        f"    {len(points)},"
    ]
    # The indices sequence 0, 2, 1 is used because of the difference between
    # the STL coordinate system and that used in POV-ray
    lines += [f"    <{p[0]}, {p[2]}, {p[1]}>," for p in points]
    lines[-1] = lines[-1][:-1]
    lines += ["  }\n  face_indices {", f"    {len(ifacets)},"]
    lines += [f"    <{f[0]}, {f[1]}, {f[2]}>," for f in ifacets]
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
    parser.add_argument('-2', '--mesh2', action='store_true', help=argtxt, dest='mesh2')
    parser.add_argument(
        '-e',
        '--encoding',
        type=str,
        help="encoding for the name of the STL object (default utf-8)",
        default='utf-8'
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument(
        '--log',
        default='warning',
        choices=['debug', 'info', 'warning', 'error'],
        help="logging level (defaults to 'warning')"
    )
    parser.add_argument('file', nargs='*', help='one or more file names')
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
    )
    if not args.file:
        parser.print_help()
        sys.exit(0)
    for fn in args.file:
        logging.info(f'Starting file "{fn}"')
        if not fn.lower().endswith('.stl'):
            w = f'the file "{fn}" is probably not an STL file, skipping'
            logging.warning(w)
            continue
        try:
            logging.info("Reading facets")
            vertices, name = stl.readstl(fn, args.encoding)
            outfn = utils.outname(fn, '.inc')
        except Exception as e:  # pylint: disable=W0703
            logging.error(f"{fn}: {e}")
            continue
        if not valid_name(name):
            ws = f'the object name "{name}" is not a valid POV-ray identifier.'
            logging.warning(ws)
            name = generate_name(name, fn)
            logging.warning(f'using "m_{name}" instead.')
        outs = f"// Generated by stl2pov {__version__}\n"
        outs += f"// on {time.asctime()}.\n"
        outs += f'// Source file name: "{fn}"\n'
        if args.mesh2:
            logging.info('generating mesh2 data.')
            outs += mesh2(name, vertices)
        else:
            logging.info('generating mesh data.')
            outs += mesh1(name, vertices)
        try:
            with open(outfn, 'w+') as of:
                logging.info(f"writing output file '{outfn}'.")
                of.write(outs)
        except Exception:
            logging.warning(f"cannot write output file '{outfn}'.")
            continue
        logging.info(f"done with file '{fn}'.")


if __name__ == '__main__':
    main(sys.argv[1:])

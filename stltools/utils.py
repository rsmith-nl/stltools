# file: utils.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2020 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2013-07-07 21:01:52  +0200
# Last modified: 2022-01-20T09:48:22+0100
"""Utilities for stltools."""

import argparse
import functools as ft
import itertools as it
import os.path
import re


class RotateAction(argparse.Action):
    """Gather rotation options."""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Create RotateAction object."""
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(RotateAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Implement rotate option."""
        rotations = getattr(namespace, "rotations", None)
        if not rotations:
            rotations = []
        rotations += [(option_string[1], values)]
        setattr(namespace, "rotations", rotations)


def outname(inname, extension, addenum=""):
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
    rv = re.sub(r"^[\s\.]+|\s+$", "", rv)
    rv = re.sub(r"\s+", "_", rv)
    if not extension.startswith("."):
        extension = "." + extension
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
    red = ((color & 0xFF0000) >> 16) / 255
    green = ((color & 0x00FF00) >> 8) / 255
    blue = (color & 0x0000FF) / 255
    return red, green, blue


def chunked(iterable, n):
    """
    Split an iterable up in chunks of length n.

    The second argument to the outer ``iter()`` is crucial to the way this works.
    See the documentation for ``iter()`` for details.
    """

    def take(n, iterable):
        return list(it.islice(iterable, n))

    return iter(ft.partial(take, n, iter(iterable)), [])

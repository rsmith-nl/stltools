# file: stl.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2012-2020 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2012-11-10 07:55:54 +0100
# Last modified: 2022-01-20T09:36:51+0100
"""Handling STL files and brep datasets."""

from . import vecops as vo
from . import utils
import datetime
import mmap
import struct


def readstl(name, encoding="utf-8"):
    """
    Read an STL file, return the vertices and the name.

    The normal vector information is *discarded* since it is often unreliable.
    Instead the normal vector is calculated from the sequence of the vertices.

    Arguments:
        name: Path of the STL file to read.
        encoding: Assume this encoding for the name of the file (defaults to UTF-8).

    Returns:
        A list of 3-tuples of float containing the vertices of the
        facets, and the name of the object as given in the STL file.
    """
    with open(name, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        vertices, name = _parsebinary(mm, encoding)
        if vertices is None:
            mm.seek(0)
            vertices, name = _parsetxt(mm, encoding)
        mm.close()
    if vertices is None:
        raise ValueError("not a valid STL file.")
    return vertices, name


def _parsebinary(m, encoding):
    """
    Parse a binary STL file.

    Arguments:
        m: A memory mapped file.
        encoding: For the name of the object.

    Returns:
        The vertices as a list of 3-tuples of floats, and the name of the object
        from the file.
    """
    data = m.read(84)
    name = ""
    points = None
    if b"facet normal" in data:
        return None, None
    name, _ = struct.unpack("<80sI", data[0:84])
    if b"COLOR" in data:
        date = datetime.datetime.now()
        name = b" ".join(
            [
                b"Unknown Binary STL",
                b"Processed: (",
                bytes(date.month),
                bytes(date.day),
                bytes(date.year),
                b")",
                b"\n",
            ]
        )
    name = name.decode(encoding)
    name = name.replace("solid ", "")
    name = name.strip("\x00 \t\n\r")
    points = [p for p in _getbp(m)]
    return points, name


def _getbp(m):
    """
    Generate points from a binary STL file.

    Arguments:
        m: A memory mapped file.

    Yields:
        The vertices as 3-tuple of floats.
    """
    fmt = "<12x9f2x"
    sz = struct.calcsize(fmt)
    buffer = m.read()
    count = len(buffer) // sz * sz
    buffer = buffer[:count]
    for p in struct.iter_unpack(fmt, buffer):
        yield tuple(p[0:3])
        yield tuple(p[3:6])
        yield tuple(p[6:])


def _parsetxt(m, encoding):
    """
    Parse a text STL file.

    Arguments:
        m: A memory mapped file.
        encoding: For the name of the object.

    Returns:
        The vertices as a list of 3-tuples of floats, and the name of the object from
        the file.
    """
    first = m.readline().decode(encoding)
    name = None
    points = None
    if first.startswith("solid") and b"facet normal" in m.readline():
        try:
            name = first.strip().split(None, 1)[1]
        except IndexError:
            name = ""
        vlines = [ln.split() for ln in _striplines(m) if ln.startswith("vertex")]
        points = [tuple(float(k) for k in j[1:]) for j in vlines]
    m.seek(0)
    return points, name


def _striplines(m):
    """
    Generate stripped lines from a memmapped text file.

    Arguments:
        m: A memory mapped file.

    Yields:
        The stripped lines of the file as text.
    """
    while True:
        v = m.readline().decode("utf-8")
        if v:
            yield v.strip()
        else:
            break


def toindexed(vertices):
    """
    Convert vertices to index format.

    Create an array of unique vertices and an array of indices into the unique
    vertax array that matches the original array.

    Arguments:
        vertices: iterable of 3-tuples of float as vertex coordinates.

    Returns:
        A list of facet indices lists and a tuple of unique vertex 3-tuples.
    """
    ix, points = vo.indexate(vertices)
    facets = tuple(tuple(j) for j in utils.chunked(ix, 3))
    return facets, points


def normals(facets, points):
    """
    Calculate normal vectors of facets.

    Arguments:
        facets: An iterable of 3-tuples facet indices into points.
        points: A tuple of 3-tuples of unique points.

    Returns:
         An tuple of indices and a tuple of unique 3-tuples representing uniqe normals.
    """
    nv = [vo.normal(points[i], points[j], points[k]) for i, j, k in facets]
    return vo.indexate(nv)


def text(name, ifacets, points, inormals, vectors):
    """
    Make an STL text representation of a brep.

    Arguments:
        name: The name of the object.
        ifacets: A tuple of indices into the points.
        points: A tuple of 3-tuples of vertex coordinates.
        inormals: A tuple of indices into the vectors list.
        vectors: A tuple of 3-tuples of normal vectors.

    Returns:
        A string containing a text representation of the brep.
    """
    fcts = list(zip(ifacets, inormals))
    ln = ["solid {}".format(name)]
    for f, n in fcts:
        ln.append(
            f"  facet normal {vectors[n][0]:.1f} {vectors[n][1]:.1f} {vectors[n][2]:.1f}"
        )
        ln.append("    outer loop")
        for v in f:
            ln.append(
                f"      vertex {points[v][0]:.1f} {points[v][1]:.1f} {points[v][2]:.1f}"
            )
        ln.append("    endloop")
        ln.append("  endfacet")
    ln.append("endsolid")
    return "\n".join(ln)


def binary(name, ifacets, points, inormals, vectors):
    """
    Make an STL binary representation of a brep.

    Arguments:
        name: The name of the object.
        ifacets: A tuple of indices into the points.
        points: A tuple of 3-tuples of vertex coordinates.
        inormals: A tuple of indices into the vectors list.
        vectors: A tuple of 3-tuples of normal vectors.

    Returns:
        A string containing a binary representation of the brep.
    """
    rc = [struct.pack("<80sI", name.encode("utf-8"), len(ifacets))]
    for fi, ni in zip(ifacets, inormals):
        data = list(vectors[ni] + points[fi[0]] + points[fi[1]] + points[fi[2]]) + [0]
        rc.append(struct.pack("<12fH", *data))
    return b"".join(rc)

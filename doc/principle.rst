==================================
The principle or reading STL files
==================================

An STL file is a boundary representation made up out of triangular
facets. Each file is supposed to contain one closed hull.

An STL file can have two formats, binary and text. The binary format
is easiest to parse, so we'll cover that first.

Binary format
~~~~~~~~~~~~~

It consists of an 84-byte header, followed by 50-byte data blocks,
each descibing a facet. Each facet contains 12 floating point values
in float format (4 bytes each), plus two padding bytes. Those padding
bytes are sometimes used for adding colors to a facet, but there are
several (ambiguous) formats for that, so we will discard that. The
floating point numbers form four groups of three values. The first
group is supposed to contain the normal vector for the facet, but is
often zero or otherwise incorrect. The other three points are the
vertices of the triangle.


Text format
~~~~~~~~~~~

The text format is quite simple. An example is given below.

.. code:

    solid test
      facet normal 0.0 -0.0 1.0
        outer loop
          vertex 0.0 0.0 1.0
          vertex 1.0 0.0 1.0
          vertex 0.0 1.0 1.0
        endloop
      endfacet
      facet normal 0.0 -0.0 1.0
        outer loop
          vertex 1.0 0.0 1.0
          vertex 1.0 1.0 1.0
          vertex 0.0 1.0 1.0
        endloop
      endfacet
      facet normal 0.0 -1.0 0.0
        outer loop
          vertex 0.0 0.0 1.0
          vertex 1.0 0.0 0.0
          vertex 1.0 0.0 1.0
        endloop
      endfacet
      facet normal 0.0 -1.0 0.0
        outer loop
          vertex 0.0 0.0 1.0
          vertex 0.0 0.0 0.0
          vertex 1.0 0.0 0.0
        endloop
      endfacet
    endsolid



Parsing
~~~~~~~

A new ``TriSurface`` object is created with optionally the name of an STL
file from which to read the data.

For each facet read, the following actions are taken. First the three
vertices are converted to numpy arrays, a,b and c using
``dtype=float``. The vectors u = b-a and v = c-b are calculated. The cross
product n = np.cross(u,v) is normalized using n /= (n*n).sum()**0.5
and added to the array of normal vectors.

Then for each of the vertices we check wether the same vertex is
already in the object-wide numpy vertex array. 

.. code-block: python

    In [1]: import numpy as np

    In [2]: t1 = np.array(np.arange(30), dtype=float).reshape((-1,3))

    In [89]: t1
    Out[89]: 
    array([[  0.,   1.,   2.],
           [  3.,   4.,   5.],
           [  6.,   7.,   8.],
           [  9.,  10.,  11.],
           [ 12.,  13.,  14.],
           [ 15.,  16.,  17.],
           [ 18.,  19.,  20.],
           [ 21.,  22.,  23.],
           [ 24.,  25.,  26.],
           [ 27.,  28.,  29.]])

    In [90]: p
    Out[90]: array([ 15.,  16.,  17.])

    In [91]: np.nonzero(p == t1)
    Out[91]: (array([5, 5, 5]), array([0, 1, 2]))

    In [92]: ind, where = np.nonzero(p == t1)

    In [93]: np.all(where == np.array([0, 1, 2]))
    Out[93]: True

    In [94]: ind[0]
    Out[94]: 5

The indices are added to a list `newi`. The edges are 2-tuples of list
indices in sorted order. They are calculated as follows;

.. code-block: python

    In [115]: newi
    Out[115]: [17, 12, 34]

    In [116]: newedges = [tuple(sorted(newi[0:2])), tuple(sorted(newi[1:3])), (newi[2], newi[0])]

    In [117]: newedges
    Out[117]: [(12, 17), (12, 34), (34, 17)]

The indices of the vertices in the TriSurface numpy vertices array,
the index of the normal vector and the edges are stored in a facet
array. This is added to the facet list.

Rendering
~~~~~~~~~

Projection
----------
This is a combination of rotations and movements of the object's
local coordinate system with respect to the global system.

This eventually yields a matrix that is used to determine where the
vertices are and wether a triangle is visible from this projection or
not. The triangles are marked accordingly

Edges
-----
Create two lists of Triangles with list comprehension, those who are
visible (tv), and those who are invisible (ti). Using these lists,
create two sets from the edge tuples of the visible (ev) and the
invisible (ei) triangles. Edge tuples that are in the intersection (ve
= ev & ei) of both sets are edges of the figure. Draw them with thick
lines. The other visible edges (ev - ve) are normal edges, draw them
in normal line thickness.



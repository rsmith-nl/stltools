=====================
STL file manipulation
=====================

The module stl.py reads both text and binary STL files and creates STL
objects. The module xform.py handles coordinate transforms and projections.

The scripts stl2pov, stl2ps and stl2pdf use this library to convert STL files
to POV-ray meshes, PostScript and PDF files respectively.

stl2pov
-------
This is a refactoring of the C version 2.x. Version 2 was too slow, basically
because it tried to do too much. This version is a straight translator. It
produces a POV-ray mesh declaration that you can use in your scenes. N.B.: you
have to instantiate the mesh as an object, give it material properties, define
a light and a camera &c.


stl2ps
------
This is a new script that produces a view of the STL object looking down
parallel to the positive Z-axis on the centre of the object. Rotating the
object is supported. Currently the output uses only grayscale and a very
simple shading algorithm. It does not draw facets that point away from the
viewer. The remaining facets are sorted back to front by average depth of
their vertices. The removal of completely occluded surfaces has been tested
and dropped as too expensive. Shadows and more sophisticated lighting effects
are not planned, but patches are welcome.

stl2pdf
-------
This is basically a variant of stl2ps using the ReportLab toolkit to generate
PDF output directly.

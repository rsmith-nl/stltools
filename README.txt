=====================
STL file manipulation
=====================

The module stl.py reads both text and binary STL files and creates STL objects.
The module xform.py handles coordinate transforms and projections.

The scripts stl2pov and stl2ps use this library to convert STL files to
POV-ray meshes and PostScript files respectively.

stl2pov 3 beta1
---------------
This is a refactoring of the C version 2.x. Version 2 was too slow, basically
because it tried to do too much. This version 3 is a straight translator. It
produces a POV-ray mesh declaration that you can use in your scenes. N.B.: you
have to instantiate the mesh as an object, give it material properties, define
a light and a camera &c.


stl2ps 1 beta1
--------------
This is a new script that produces a view of the STL object looking down
parallel to the positive Z-axis on the centre of the object. Rotating the
object is supported. Currently the output uses only grayscale and a very
simple shading algorithm. It does not draw facets that point away from the
viewer. The remaining facets are sorted back to front by average depth of
their vertices. Colors is a possible enhancement, as is the removal of
completely occluded surfaces. Shadows and more sophisticated lighting effects
are not planned, but patches are welcome.

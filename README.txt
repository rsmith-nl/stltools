===================================
STL file manipulation with stltools
===================================

:Author: Roland Smith

The stltools module reads both text and binary STL files and creates STL
objects. It also handles coordinate transforms and projections.

The scripts stl2pov, stl2ps and stl2pdf use this library to convert STL files
to POV-ray meshes, PostScript and PDF files respectively.

stl2pov
-------
This is a refactoring of the C version 2.x. Version 2 was too slow, basically
because it tried to do too much. This version is a straight translator.
However, the speed of the method to create a POV-ray mesh2 object was much
improved.  It produces a POV-ray mesh or mesh2 declaration that you can use in
your scenes. N.B.: you still have to instantiate the mesh as an object, give
it material properties, define a light and a camera &c.

    usage: stl2pov.py [-h] [-2,--mesh2] [-v] [file [file ...]]

    Program for converting an STL file into a POV-ray mesh or mesh2.

    positional arguments:
    file           one or more file names

    optional arguments:
    -h, --help     show this help message and exit
    -2,--mesh2     generate a mesh2 object (slow on big files)
    -v, --version  show program's version number and exit


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

    usage: stl2ps infile [outfile] [transform [transform ...]]
    where [transform] is [x number|y number|z number]


stl2pdf
-------
This is basically a variant of stl2ps using the cairo library to generate
PDF output directly. It requires the cairo library and its Python binding.

    usage: stl2pdf infile [outfile] [transform [transform ...]]
    where [transform] is [x number|y number|z number]


stlinfo
-------
This program prints some information about the STL file, like the name of the
object, its bounding box and the number of facets. Optionally it can also list
an STL text version of the file. This way stlinfo can be used to convert a
binary STL file to a text version.

    usage: stlinfo.py [-h] [-t] [-b] [-v] [file [file ...]]

    Reads an STL file and prints information about the object or a text
    representation of the object in the file.

    positional arguments:
    file           one or more file names

    optional arguments:
    -h, --help     show this help message and exit
    -t, --text     print text representation of the file
    -b, --binary   write binary representation of the file
    -v, --version  show program's version number and exit


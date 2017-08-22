STL file manipulation with stltools
###################################

:author: Roland Smith

.. Last modified: 2017-08-22 17:45:36 +0200
.. vim:fileencoding=utf-8:ft=rst

The stltools module reads both text and binary STL files and creates STL
objects. It also handles coordinate transforms and projections.

The scripts stl2pov, stl2ps and stl2pdf use this library to convert STL files
to POV-ray meshes, PostScript and PDF files respectively.

.. note::
    The ``master`` branch is for releases. Development is done in the
    ``develop`` branch.

stl2pov
-------
This is a refactoring of the C version 2.x. Version 2 was too slow, basically
because it tried to do too much. This version is a straight translator.
However, the speed of the method to create a POV-ray mesh2 object was much
improved.  It produces a POV-ray mesh or mesh2 declaration that you can use in
your scenes. N.B.: you still have to instantiate the mesh as an object, give
it material properties, define a light and a camera &c.::


    usage: stl2pov.py [-h] [-2,--mesh2] [-v] [--log {debug,info,warning,error}]
                    [file [file ...]]

    Program for converting an STL file into a POV-ray mesh or mesh2.

    positional arguments:
    file                  one or more file names

    optional arguments:
    -h, --help            show this help message and exit
    -2,--mesh2            generate a mesh2 object (slow on big files)
    -v, --version         show program's version number and exit
    --log {debug,info,warning,error}
                            logging level (defaults to 'warning')

Version 4 marked the switch to Python 3 and an internal reworking of the code.
Among other things, the logging module is now used.

Up to version 5, stl2pov had used the object name in the STL file as the
identifier for the mesh. But it was pointed out to me that often the object
name often isn't a valid identifier.  So in version 5, the oject name is
checked if it would be a valid identifier.  If not, a valid identifier is
generated based on the object name. If the object name is empty, the
identifier is based on the filename.


stl2ps
------
This is a new script that produces a view of the STL object looking down
parallel to the positive Z-axis on the centre of the object. Rotating the
object is supported. Currently the output uses only grayscale and a very
simple shading algorithm. It does not draw facets that point away from the
viewer. The remaining facets are sorted back to front by average depth of
their vertices. The removal of completely occluded surfaces has been tested
and dropped as too expensive. Shadows and more sophisticated lighting effects
are not planned, but patches are welcome.::

    usage: stl2ps.py [-h] [--log {debug,info,warning,error}] [-c CANVAS_SIZE]
                    [-f FG] [-b BG] [-o OUTFILE] [-x X] [-y Y] [-z Z]
                    file

    Program for converting a view of an STL file into a PostScript file. Using the
    -x, -y and -z options you can rotate the object around these axis. Subsequent
    rotations will be applied in the order they are given on the command line.
    Note that the object will be automatically centered and scaled to fit in the
    picture.

    positional arguments:
    file                  name of the file to process

    optional arguments:
    -h, --help            show this help message and exit
    --log {debug,info,warning,error}
                            logging level (defaults to 'warning')
    -c CANVAS_SIZE, --canvas CANVAS_SIZE
                            canvas size, defaults to 200 PostScript points
    -f FG, --foreground FG
                            foreground color in 6-digit hexdecimal RGB (default
                            E6E6E6)
    -b BG, --background BG
                            background color in 6-digit hexdecimal RGB (default
                            white FFFFFF)
    -o OUTFILE, --output OUTFILE
                            output file name
    -x X                  rotation around X axis in degrees
    -y Y                  rotation around Y axis in degrees
    -z Z                  rotation around Z axis in degrees


stl2pdf
-------
This is basically a variant of stl2ps using the cairo library to generate
PDF output directly. It requires the cairo library and its Python binding.::

    usage: stl2pdf.py [-h] [--log {debug,info,warning,error}] [-c CANVAS_SIZE]
                    [-f FG] [-b BG] [-o OUTFILE] [-x X] [-y Y] [-z Z]
                    file

    Program for converting a view of an STL file into a PDF file. Using the -x, -y
    and -z options you can rotate the object around these axis. Subsequent
    rotations will be applied in the order they are given on the command line.
    Note that the object will be automatically centered and scaled to fit in the
    picture.

    positional arguments:
    file                  name of the file to process

    optional arguments:
    -h, --help            show this help message and exit
    --log {debug,info,warning,error}
                            logging level (defaults to 'warning')
    -c CANVAS_SIZE, --canvas CANVAS_SIZE
                            canvas size, defaults to 200 PostScript points
    -f FG, --foreground FG
                            foreground color in 6-digit hexdecimal RGB (default
                            E6E6E6)
    -b BG, --background BG
                            background color in 6-digit hexdecimal RGB (default
                            FFFFFF)
    -o OUTFILE, --output OUTFILE
                            output file name
    -x X                  rotation around X axis in degrees
    -y Y                  rotation around Y axis in degrees
    -z Z                  rotation around X axis in degrees


stlinfo
-------
This program prints some information about the STL file, like the name of the
object, its bounding box and the number of facets. Optionally it can also list
an STL text version of the file. This way stlinfo can be used to convert a
binary STL file to a text version.::

    usage: stlinfo.py [-h] [-t] [-b] [-v] [--log {debug,info,warning,error}]
                    [file [file ...]]

    Read an STL file and print information about the object. Optionally print a
    text representation of the object. It can also write a binary STL version of
    the object.

    positional arguments:
    file                  one or more file names

    optional arguments:
    -h, --help            show this help message and exit
    -t, --text            print text representation of the file
    -b, --binary          write binary representation of the file
    -v, --version         show program's version number and exit
    --log {debug,info,warning,error}
                            logging level (defaults to 'warning')

Usage
=====

It is not *necessary* to install these scripts.
You should be able to run the scripts from the ``stltools`` directory.


Installation
============

Run the following command to install the module and the scripts.

.. code-block:: sh

    # python setup.py install

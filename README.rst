STL file manipulation with stltools
###################################

:date: 2015-08-22
:author: Roland Smith

.. vim:fileencoding=utf-8:ft=rst

The stltools modules can read both text and binary STL files and extract the
geometry from them. It also handles coordinate transforms and projections.

The scripts stl2pov, stl2ps and stl2pdf use this library to convert STL files
to POV-ray meshes, PostScript and PDF files respectively.

stl2pov
-------
This is a refactoring of the C version 2.x. Version 2 was too slow, basically
because it tried to do too much. This version is a straight translator.
However, the speed of the method to create a POV-ray mesh2 object was much
improved.  It produces a POV-ray mesh or mesh2 declaration that you can use in
your scenes. N.B.: you still have to instantiate the mesh as an object, give
it material properties, define a light and a camera &c.::

    usage: stl2pov.py [-h] [-2,--mesh2] [-v] [--log {info,debug,warning,error}]
                    [file [file ...]]

    Program for converting an STL file into a POV-ray mesh or mesh2.

    positional arguments:
    file                  one or more file names

    optional arguments:
    -h, --help            show this help message and exit
    -2,--mesh2            generate a mesh2 object (slow on big files)
    -v, --version         show program's version number and exit
    --log {info,debug,warning,error}
                            logging level (defaults to 'warning')


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
                    [-o OUTFILE] [-x X] [-y Y] [-z Z]
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
                    [-o OUTFILE] [-x X] [-y Y] [-z Z]
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

    Reads an STL file and prints information about the object and optionally a
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


Requirements
============

General requirements;

* Python 3 (tested with 3.4)
* numpy (tested with 1.9.2)

For ``stl2pdf``, the cairo_ graphics library (tested with version 1.14.2) and
its Python bindings (tested with version 1.10.0) are required.

.. _cairo: http://cairographics.org/

For running the tests, nosetests_ is required.

.. _nosetests: https://nose.readthedocs.org/en/latest/index.html


Installation
============

Run the following command to install the module and the scripts.

.. code-block:: console

    # python3 setup.py install --record stltools-files.txt

Keep the file ``stltools-files.txt``; it shows you which files to remove to
completely uninstall the program.


Testing the code
================

The directory ``test`` contains tests (using nosetests_) for most of the code.

To run the tests;

.. code-block:: console

    > cd test/
    > nosetests -v

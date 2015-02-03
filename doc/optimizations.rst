Speed optimizations
###################

:date: 2015-02-03
:tags: tuning
:author: Roland Smith

Based on the Libre3D PHP port which was faster, I was motivated to to some
speed tuning. :-)

Output tuning
=============

A simple change in the mesh1 function in stl2pov.py reduced the time to
process test/headrest_mesh.stl from 11.67 to 7.5 seconds!

Before:

    ./stl2pov.py test/headrest_mesh.stl
    [0:00:00.00]: Starting file "test/headrest_mesh.stl"
    [0:00:00.00]: Reading facets
    [0:00:01.99]: Generating mesh data
    [0:00:11.17]: Writing output file "headrest_mesh.inc"
    [0:00:11.67]: Done with file "test/headrest_mesh.stl"

After:

    [0:00:00.00]: Starting file "test/headrest_mesh.stl"
    [0:00:00.00]: Reading facets
    [0:00:01.54]: Generating mesh data
    [0:00:07.08]: Writing output file "headrest_mesh.inc"
    [0:00:07.51]: Done with file "test/headrest_mesh.stl"

The difference in code was;

.. code-block:: diff

    diff --git a/stl2pov.py b/stl2pov.py
    index 872382b..8c0287e 100755
    --- a/stl2pov.py
    +++ b/stl2pov.py
    @@ -42,15 +42,13 @@ def mesh1(name, vertices):
        :vertices: An (N,3) numpy array containing the vertex data.
        :returns: a string representation of a POV-ray mesh object.
        """
    -    facets = vertices.reshape((-1, 3, 3))
    +    facets = vertices.reshape((-1, 9))
        lines = ["# declare m_{} = mesh {{".format(name.replace(' ', '_'))]
    -    sot = "  triangle {"
        # The indices sequence 1, 0, 2 is used because of the difference between
        # the STL coordinate system and that used in POV-ray.
    -    fc = "    <{1}, {0}, {2}>,"
    -    for (a, b, c) in facets:
    -        lines += [sot, fc.format(*a), fc.format(*b),
    -                  fc.format(*c)[:-1], "  }"]
    +    fct = "  triangle {{\n    <{1}, {0}, {2}>,\n    <{4}, {3}, {5}>,\n" \
    +          "    <{7}, {6}, {8}>\n  }}"
    +    lines += [fct.format(*f) for f in facets]
        lines += ['}']
        return '\n'.join(lines)

Replacing three format calls with one (and therefore also a shorter join) made
all the difference.

Intrigued by this I decided to look into the speed of text formatting in
Python. And the results were interesting.

.. code-block:: python

    In [34]: %timeit '<{}, {}, {}>,'.format(n, m, k)
    100000 loops, best of 3: 5.37 µs per loop

    In [35]: %timeit '<%f %f %f>,' % (n, m, k)
    100000 loops, best of 3: 1.66 µs per loop

    In [36]: %timeit '<{1}, {0}, {2}>,'.format(n, m, k)
    1000000 loops, best of 3: 354 ns per loop

    In [37]: %timeit '<{1!s}, {0!s}, {2!s}>,'.format(n, m, k)
    1000000 loops, best of 3: 357 ns per loop

    In [38]: '<{1}, {0}, {2}>,'.format(n, m, k)
    Out[38]: '<138.768768311, -793.1467, 69.9136581421>,'

    In [39]: '<{1!s}, {0!s}, {2!s}>,'.format(n, m, k)
    Out[39]: '<138.768768311, -793.1467, 69.9136581421>,'

    In [40]: %timeit '<{1:.6e}, {0:.6e}, {2:.6e}>,'.format(n, m, k)
    100000 loops, best of 3: 4.13 µs per loop

    In [41]: '<{1:.6e}, {0:.6e}, {2:.6e}>,'.format(n, m, k)
    Out[41]: '<1.387688e+02, -7.931467e+02, 6.991366e+01>,'


So, initially old-fashioned string formatting ([35]) seems faster than the
``format`` method ([34]). But if you specify the positional arguments (as in
[36]), ``format`` becomes *much faster*. Using a format spec ([40]) slows
things down significantly, though.

Writing files directly
======================

Instead of joining a list of lines and writing that, I tried writing each line
directly. This proved marginally faster on smaller files but marginally slower
on large files.

What I haven't tried is using the ``file.writelines()`` method.

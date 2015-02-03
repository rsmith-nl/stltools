Speed optimizations
###################

:date: 2015-02-03
:tags: 
:author: Roland Smith

Based on the Libre3D PHP port, I was motivated to to some speed tuning.

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


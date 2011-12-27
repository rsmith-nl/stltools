from stl import *
#import xform

# Make the vertices
v1 = Vertex(0,0,1)
v2 = Vertex(1,0,1)
v3 = Vertex(1,0,0)
v4 = Vertex(0,0,0)
v5 = Vertex(0,1,1)
v6 = Vertex(1,1,1)
v7 = Vertex(1,1,0)
v8 = Vertex(0,1,0)

# Create the STL object, add the facets
cube = Surface()
cube.name = 'cube'
# Front facets (looking from Z+)
cube.addfacet(v1, v2, v5, None)
cube.addfacet(v2, v6, v5, None)
# Bottom facets
cube.addfacet(v1, v3, v2, None)
cube.addfacet(v1, v4, v3, None)
# Top facets
cube.addfacet(v5, v6, v7, None)
cube.addfacet(v5, v7, v8, None)
# Back facets
cube.addfacet(v4, v8, v3, None)
cube.addfacet(v8, v7, v3, None)
# Right facets
cube.addfacet(v2, v3, v6, None)
cube.addfacet(v6, v3, v7, None)
# Left facets
cube.addfacet(v1, v5, v4, None)
cube.addfacet(v4, v5, v8, None)

# Rotate the cube
#tr = xform.Xform()
#tr.roty(15)
#tr.rotx(10)
#cube.xform(tr)

# Print it
print cube

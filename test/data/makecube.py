# file: makecube.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2012-01-01 13:12:08 +0100
# Last modified: 2015-05-06 21:48:01 +0200

import logging
import sys
sys.path.insert(0, '..')
sys.path.insert(0, '.')

import numpy as np
from stltools import matrix as mx
from stltools import stl
from stltools import vecops as vo

logging.basicConfig(level='INFO', format='%(levelname)s: %(message)s')
logging.info('creating facet data')
vertices = np.array([[0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 0, 0], [0, 1, 1],
                     [1, 1, 1], [1, 1, 0],  [0, 1, 0]], np.float32)
facets = np.array([[0, 1, 4], [1, 5, 4], [0, 2, 1],  [0, 3, 2],  [4, 5, 6],
                   [4, 6, 7],  [3, 7, 2],  [7, 6, 2],  [1, 2, 5],  [5, 2, 6],
                   [0, 4, 3],  [3, 4, 7]], np.uint16)
logging.info('calculating normals')
ni, normals = stl.normals(facets, vertices)

logging.info('vertices:\n{}'.format(vertices))
logging.info('facets:\n{}'.format(facets))
logging.info('normals:\n{}'.format(normals))
logging.info('normal indices:\n{}'.format(ni))

logging.info('creating text STL data')
txtdata = stl.text('cube-txt', facets, vertices, ni, normals)
try:
    with open('cube-txt.stl', 'w') as stlf:
        stlf.write(txtdata)
    logging.info('wrote text STL file cube-txt.stl')
except IOError as e:
    logging.error('unable to write cube-txt.stl; {}'.format(e))

logging.info('creating binary STL data')
bindata = stl.binary('cube-bin', facets, vertices, ni, normals)
try:
    with open('cube-bin.stl', 'wb') as stlf:
        stlf.write(bindata)
    logging.info('wrote binary STL file cube-bin.stl')
except IOError as e:
    logging.error('unable to write cube-txt.bin; {}'.format(e))


tr = mx.concat(mx.rotx(30), mx.roty(20))
nv = vo.xform(tr, vertices)
nn = vo.xform(tr, normals)

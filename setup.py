# -*- coding: utf-8 -*-
# Installation script for stltools
#
# R.F. Smith <rsmith@xs4all.nl>
# $Date$

from distutils.core import setup
from sys import argv
import os

_scripts = ['stl2pov.py', 'stl2ps.py', 'stl2pdf.py', 'stlinfo.py']

with open('README.txt') as f:
    ld = f.read()

# Remove the extensions from the scripts for UNIX-like systems.
if os.name is 'posix' and ('install' in argv or 'build' in argv):
    outnames = [s[:-3] for s in _scripts]
    for old, new in zip(_scripts, outnames):
        os.link(old, new)
    _scripts = outnames

setup(name='stltools',
      version='$Revision$'[11:-2],
      license='BSD',
      description='Programs to read and convert STL files.',
      author='Roland Smith', author_email='rsmith@xs4all.nl',
      url='http://rsmith.home.xs4all.nl/software/py-stl-stl2pov.html',
      scripts=_scripts,
      provides='stltools', packages=['stltools'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Manufacturing',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering'
                   ],
      long_description=ld
      )

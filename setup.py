# -*- coding: utf-8 -*-
# Installation script for stltools
#
# R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2015-05-04 22:32:59 +0200

from distutils.core import setup
import os

_scripts = ['stl2pov.py', 'stl2ps.py', 'stl2pdf.py', 'stlinfo.py']

with open('README.rst') as f:
    ld = f.read()

# Remove the extensions from the scripts for UNIX-like systems.
if os.name is 'posix':
    outnames = [s[:-3] for s in _scripts]
    try:
        for old, new in zip(_scripts, outnames):
            os.link(old, new)
    except OSError:
        pass
    _scripts = outnames

setup(name='stltools',
      version='3.3',
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
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering'
                   ],
      long_description=ld
      )

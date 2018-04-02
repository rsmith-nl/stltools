# -*- coding: utf-8 -*-
# Installation script for stltools
#
# R.F. Smith <rsmith@xs4all.nl>
# Last modified: 2018-04-02 10:31:28 +0200

from setuptools import setup
import os
from stltools import __version__

_scripts = ['stl2pov.py', 'stl2ps.py', 'stl2pdf.py', 'stlinfo.py']

with open('README.rst', encoding='utf-8') as f:
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
      version=__version__,
      license='BSD',
      description='Programs to read and convert STL files.',
      author='Roland Smith',
      author_email='rsmith@xs4all.nl',
      url='https://rsmith.home.xs4all.nl/software/stltools.html',
      install_requires=['numpy>=1.7.0'],
      extras_require={
          'PDF':  ["pycairo>=1.10.0"],
          'test': ["nose>=1.3.0"],
      },
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

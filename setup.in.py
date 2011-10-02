# -*- coding: utf-8 -*-
# Installation script for stl2pov and friends
#
# R.F. Smith <rsmith@xs4all.nl>
# Time-stamp: <2011-10-02 17:09:51 rsmith>

from distutils.core import setup

with open('README.txt') as file:
    ld = file.read()


setup(name='py-stl',
      version='VERSION',
      license='BSD',
      description='Programs to read and convert STL files.',
      author='Roland Smith', author_email='rsmith@xs4all.nl',
      url='http://www.xs4all.nl/~rsmith/software/',
      scripts=['stl2pov', 'stl2ps', 'stl2pdf'],
      provides='pystl', py_modules=['stl','xform'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Manufacturing',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering'
                   ],
      long_description = ld
      )

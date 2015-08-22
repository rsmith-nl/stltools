# file: test_utils.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-08-22 20:18:04 +0200
# Last modified: 2015-08-22 20:55:33 +0200

"""Tests for the utils module.

Run this test only with nosetests-3.4 -v test_utils.py
Run all tests with: nosetests-3.4 -v
"""

import os
import sys
import numpy as np
from nose.tools import raises

sys.path.insert(1, '..')

import stltools.utils as utils


def test_outnames():
    assert utils.outname('foo', 'bar') == 'foo.bar'
    assert utils.outname('../foo', 'bar') == 'foo.bar'
    assert utils.outname('/../foo', 'bar', addenum='1') == 'foo1.bar'
    assert utils.outname('.foo', 'bar') == 'foo.bar'
    assert utils.outname('foo ', 'bar') == 'foo.bar'
    assert utils.outname('/home/bla/foo ', 'bar') == 'foo.bar'

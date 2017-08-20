# file: test_utils.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-08-22 20:18:04 +0200
# Last modified: 2016-06-11 00:45:23 +0200

"""Tests for the utils module.

Run this test only with py.test-3.5 -v test_utils.py
Run all tests with: py.test-3.5 -v
"""

import stltools.utils as utils


def test_outnames():
    assert utils.outname('foo', 'bar') == 'foo.bar'
    assert utils.outname('../foo', 'bar') == 'foo.bar'
    assert utils.outname('/../foo', 'bar', addenum='1') == 'foo1.bar'
    assert utils.outname('.foo', 'bar') == 'foo.bar'
    assert utils.outname('foo ', 'bar') == 'foo.bar'
    assert utils.outname('/home/bla/foo ', 'bar') == 'foo.bar'

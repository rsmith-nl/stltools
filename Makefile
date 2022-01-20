# file: Makefile
# vim:fileencoding=utf-8:fdm=marker:ft=make
#
# Copyright © 2011 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2011-09-23T00:14:59+02:00
# Last modified: 2022-01-20T09:43:35+0100
.PHONY: help clean dist tests
.SUFFIXES: .py

SCRIPTS=stl2ps stl2pov stl2pdf stlinfo

help::
	@echo "You can use one of the following commands:"
	@echo "  clean -- Remove generated files"
	@echo "  tests -- Run code tests using py.test."

clean::
	rm -rf ${SCRIPTS}
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

tests::
	py.test -v test/test*.py

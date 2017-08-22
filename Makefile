.PHONY: help clean dist tests
.SUFFIXES: .py

SCRIPTS=stl2ps stl2pov stl2pdf stlinfo

help::
	@echo "You can use one of the following commands:"
	@echo "  clean -- Remove generated files"
	@echo "  dist --  Create distribution file"
	@echo "  clean -- Update keywords in files."
	@echo "  tests -- Run code tests using py.test."

clean::
	rm -rf dist build backup-*.tar.gz MANIFEST ${SCRIPTS}
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

dist::
	python setup.py sdist --format=zip
	rm -f ${SCRIPTS}


tests::
	cd test; py.test-3.6 -v test*.py

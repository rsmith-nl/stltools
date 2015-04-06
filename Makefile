.PHONY: help clean dist refresh
.SUFFIXES: .py

SCRIPTS=stl2ps stl2pov stl2pdf stlinfo

help::
	@echo "You can use one of the following commands:"
	@echo "  clean -- Remove generated files"
	@echo "  dist --  Create distribution file"
	@echo "  clean -- Update keywords in files."

clean::
	rm -rf dist build backup-*.tar.gz MANIFEST ${SCRIPTS}
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

dist::
	python setup.py sdist --format=zip
	rm -f ${SCRIPTS}

refresh::
	update-all-keywords

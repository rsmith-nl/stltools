.PHONY: all install dist clean
.SUFFIXES: .py

BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin
PYSITE!=python -c 'import site; print site.getsitepackages()[0]'
VER!=grep Revision stl2pov.py | cut -d ' ' -f 4

help::
	@echo "You can use one of the following commands:"
	@echo "  install -- install the package system-wide"
	@echo "  deinstall -- remove the system-wide installation"
	@echo "  clean -- remove generated files"

all: install

install::
# Let Python do the install work.
	python setup.py install
	rm -rf build

deinstall::
	rm -f ${PYSITE}/stltools
	rm -f $(BINDIR)/stl2ps $(BINDIR)/stl2pov $(BINDIR)/stl2pdf $(BINDIR)/stlinfo

clean::
	rm -rf dist build backup-*.tar.gz *.pyc MANIFEST stl2ps stl2pov stl2pdf stlinfo

#EOF
# The specifications below are for the maintainer only.
CUTLINE!=grep -n '\#[^E]*EOF' Makefile | cut -d ':' -f 1

dist::
	mv Makefile Makefile.orig
	head -n ${CUTLINE} Makefile.orig >Makefile
	python setup.py sdist --format=zip
	mv Makefile.orig Makefile

.PHONY: all install dist clean
.SUFFIXES: .py

BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin
PYSITE!=python -c 'import site; print site.getsitepackages()[0]'

help::
	@echo "You can use one of the following commands:"
	@echo "  install -- install the package system-wide"
	@echo "  deinstall -- remove the system-wide installation"

all: install

install::
# Let Python do most of the install work.
	python setup.py install
# Lose the extension; this is UNIX. :-)
	mv $(BINDIR)/stl2ps.py $(BINDIR)/stl2ps
	mv $(BINDIR)/stl2pov.py $(BINDIR)/stl2pov
	mv $(BINDIR)/stl2pdf.py $(BINDIR)/stl2pdf
	mv $(BINDIR)/stlinfo.py $(BINDIR)/stlinfo
	rm -rf build

deinstall::
	rm -f ${PYSITE}/stltools
	rm -f $(BINDIR)/stl2ps $(BINDIR)/stl2pov $(BINDIR)/stl2pdf $(BINDIR)/stlinfo

clean::
	rm -rf dist build backup-*.tar.gz *.pyc ${ALL} MANIFEST

#EOF
# The specifications below are for the maintainer only.
CUTLINE!=grep -n '\#[^E]*EOF' Makefile | cut -d ':' -f 1

dist: ${ALL}
	mv Makefile Makefile.orig
	head -n ${CUTLINE} Makefile.orig >Makefile
	python setup.py sdist --format=zip
	mv Makefile.orig Makefile

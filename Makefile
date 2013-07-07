.PHONY: all install dist clean backup deinstall check
.SUFFIXES: .py

BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin
PYSITE!=python -c 'import site; print site.getsitepackages()[0]'

help::
	@echo "You can use one of the following commands:"
	@echo "  install -- install the package system-wide"
	@echo "  deinstall -- remove the system-wide installation"
#beginskip
	@echo "  dist -- create a distribution file"
	@echo "  clean -- remove all generated files"
	@echo "  backup -- make a complete backup"
#endskip


install: ${ALL}
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to install the program!"; \
		exit 1; \
	fi
# Let Python do most of the install work.
	python setup.py install
# Lose the extension; this is UNIX. :-)
	mv $(BINDIR)/stl2ps.py $(BINDIR)/stl2ps
	mv $(BINDIR)/stl2pov.py $(BINDIR)/stl2pov
	mv $(BINDIR)/stl2pdf.py $(BINDIR)/stl2pdf
	mv $(BINDIR)/stlinfo.py $(BINDIR)/stlinfo
	rm -rf build

deinstall::
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to deinstall the program!"; \
		exit 1; \
	fi
	rm -f ${PYSITE}/brep
	rm -f $(BINDIR)/stl2ps $(BINDIR)/stl2pov $(BINDIR)/stl2pdf $(BINDIR)/stlinfo

#beginskip
dist: ${ALL}
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
	python setup.py sdist --format=zip
	mv Makefile.org Makefile
	rm -f MANIFEST
	cd dist ; sha256 stltools-* >../port/stltools/distinfo 
	cd dist ; ls -l stltools-* | awk '{printf "SIZE (%s) = %d\n", $$9, $$5};' >>../port/stltools/distinfo 

clean::
	rm -rf dist build backup-*.tar.gz *.pyc ${ALL} MANIFEST
	rm -f port/stltools/distinfo

backup::
	sh tools/genbackup

.git/hooks/post-commit: tools/post-commit
	install -m 755 $> $@
#endskip

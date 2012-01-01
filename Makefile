.PHONY: all install dist clean backup deinstall check
.SUFFIXES: .ps .pdf .py

#beginskip
ALL = stl2pov.1 stl2pov.1.pdf stl2ps.1 stl2ps.1.pdf stl2pdf.1 stl2pdf.1.pdf stlinfo.1 stlinfo.1.pdf setup.py stl2ps.py stl2pdf.py stl2pov.py stlinfo.py
SRCS=setup.in.py stl2pdf.in.py stl2ps.in.py xform.py stl.py stl2pov.in.py stlinfo.in.py
all: ${ALL} .git/hooks/post-commit
#endskip
BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin
PYSITE!=python -c 'import site; print site.getsitepackages()[0]'

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
#Install the manual pages.
	gzip -c stl2ps.1 >stl2ps.1.gz
	gzip -c stl2pov.1 >stl2pov.1.gz
	gzip -c stl2pdf.1 >stl2pdf.1.gz
	gzip -c stlinfo.1 >stlinfo.1.gz
	install -m 644 stl2ps.1.gz stl2pov.1.gz stl2pdf.1.gz stlinfo.1.gz $(MANDIR)/man1
	rm -f stl2ps.1.gz stl2pov.1.gz stl2pdf.1.gz stlinfo.1.gz

deinstall::
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to deinstall the program!"; \
		exit 1; \
	fi
	rm -f ${PYSITE}/stl.py*
	rm -f ${PYSITE}/xform.py*
	rm -f $(BINDIR)/stl2ps $(BINDIR)/stl2pov $(BINDIR)/stl2pdf $(BINDIR)/stlinfo
	rm -f $(MANDIR)/man1/stl2ps.1* $(MANDIR)/man1/stl2pdf.1*
	rm -f $(MANDIR)/man1/stlinfo.1* $(MANDIR)/man1/stl2pov.1*

#beginskip
dist: ${ALL}
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
	python setup.py sdist --format=zip
	mv Makefile.org Makefile
	rm -f MANIFEST
	sed -f tools/replace.sed port/py-stl/Makefile.in >port/py-stl/Makefile
	cd dist ; sha256 py-stl-* >../port/py-stl/distinfo 
	cd dist ; ls -l py-stl-* | awk '{printf "SIZE (%s) = %d\n", $$9, $$5};' >>../port/py-stl/distinfo 

clean::
	rm -rf dist build backup-*.tar.gz *.pyc ${ALL} MANIFEST
	rm -f port/py-stl/Makefile port/py-stl/distinfo

backup::
	sh tools/genbackup

check: .IGNORE
	pylint -i y --rcfile=tools/pylintrc ${SRCS}

.git/hooks/post-commit: tools/post-commit
	install -m 755 $> $@

tools/replace.sed: .git/index
	tools/post-commit

setup.py: setup.in.py tools/replace.sed
	sed -f tools/replace.sed setup.in.py >$@

stl2ps.py: stl2ps.in.py tools/replace.sed
	sed -f tools/replace.sed stl2ps.in.py >$@
	chmod 755 $@

stl2pdf.py: stl2pdf.in.py tools/replace.sed
	sed -f tools/replace.sed stl2pdf.in.py >$@
	chmod 755 $@

stl2pov.py: stl2pov.in.py tools/replace.sed
	sed -f tools/replace.sed stl2pov.in.py >$@
	chmod 755 $@

stlinfo.py: stlinfo.in.py tools/replace.sed
	sed -f tools/replace.sed stlinfo.in.py >$@
	chmod 755 $@

stl2ps.1: stl2ps.1.in tools/replace.sed
	sed -f tools/replace.sed stl2ps.1.in >$@

stl2pov.1: stl2pov.1.in tools/replace.sed
	sed -f tools/replace.sed stl2pov.1.in >$@

stl2pdf.1: stl2pdf.1.in tools/replace.sed
	sed -f tools/replace.sed stl2pdf.1.in >$@

stlinfo.1: stlinfo.1.in tools/replace.sed
	sed -f tools/replace.sed stlinfo.1.in >$@

stl2ps.1.pdf: stl2ps.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps

stl2pov.1.pdf: stl2pov.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps

stl2pdf.1.pdf: stl2pdf.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps

stlinfo.1.pdf: stlinfo.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps
#endskip

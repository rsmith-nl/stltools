.PHONY: all install dist clean backup
.SUFFIXES: .ps .pdf .py

#beginskip
ALL = stl2ps.1 stl2ps.1.pdf stl2pdf.1 stl2pdf.1.pdf setup.py stl2ps.py stl2pdf.py stl2pov.py stl2txt.py
all: ${ALL}
#endskip
BASE=/usr/local
MANDIR=$(BASE)/man
BINDIR=$(BASE)/bin

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
	mv $(BINDIR)/stl2txt.py $(BINDIR)/stl2txt
	rm -rf build
#Install the manual pages.
	gzip -c stl2ps.1 >stl2ps.1.gz
	gzip -c stl2pdf.1 >stl2pdf.1.gz
	install -m 644 stl2ps.1.gz stl2pdf.1.gz $(MANDIR)/man1
	rm -f stl2ps.1.gz stl2pdf.1.gz

#beginskip
dist: ${ALL}
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
	python setup.py sdist --format=zip
	mv Makefile.org Makefile
	rm -f MANIFEST

clean::
	rm -rf dist build backup-*.tar.gz *.pyc ${ALL} MANIFEST

backup::
	sh tools/genbackup

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

stl2txt.py: stl2txt.in.py tools/replace.sed
	sed -f tools/replace.sed stl2txt.in.py >$@
	chmod 755 $@

stl2ps.1: stl2ps.1.in tools/replace.sed
	sed -f tools/replace.sed stl2ps.1.in >$@

stl2pdf.1: stl2pdf.1.in tools/replace.sed
	sed -f tools/replace.sed stl2pdf.1.in >$@

stl2ps.1.pdf: stl2ps.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps

stl2pdf.1.pdf: stl2pdf.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps
#endskip

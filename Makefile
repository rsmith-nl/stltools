.PHONY: all install dist clean backup
.SUFFIXES: .ps .pdf .py

#beginskip
ALL = stl2ps.1 stl2ps.1.pdf setup.py stl2ps stl2pov
all: ${ALL}
#endskip
MANBASE=/usr/local/man

install: stl2ps.1 setup.py stl2ps stl2pov
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to install the program!"; \
		exit 1; \
	fi
	python setup.py install
	rm -rf build
	gzip -k stl2ps.1
	install -m 644 stl2ps.1.gz $(MANBASE)/man1
	rm -f stl2ps.1.gz

#beginskip
dist: ${ALL}
	mv Makefile Makefile.org
	awk -f tools/makemakefile.awk Makefile.org >Makefile
	python setup.py sdist
	mv Makefile.org Makefile
	rm -f MANIFEST

clean::
	@rm -rf dist build py-stl-*.tar.gz *.pyc ${ALL} MANIFEST

backup::
	@sh tools/genbackup

.git/hooks/post-commit: tools/post-commit
	install -m 755 $> $@

tools/replace.sed: .git/index
	tools/post-commit

setup.py: setup.in.py tools/replace.sed
	sed -f tools/replace.sed setup.in.py >$@

stl2ps: stl2ps.in.py tools/replace.sed
	sed -f tools/replace.sed stl2ps.in.py >$@

stl2pov: stl2pov.in.py tools/replace.sed
	sed -f tools/replace.sed stl2pov.in.py >$@

stl2ps.1: stl2ps.1.in tools/replace.sed
	sed -f tools/replace.sed stl2ps.1.in >$@

stl2ps.1.pdf: stl2ps.1
	mandoc -Tps $> >$*.ps
	epspdf $*.ps
	rm -f $*.ps
#endskip

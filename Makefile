.PHONY: all install dist clean backup

all: 
	@tools/post-commit

install: all
	@if [ `id -u` != 0 ]; then \
		echo "You must be root to install the program!"; \
		exit 1; \
	fi
	@python setup.py install

dist::
	@python setup.py sdist

clean::
	@rm -rf dist build py-stl-*.tar.gz *.pyc

backup::
	@sh tools/genbackup

# Copyright (c) 2010-2020 Daniele Varrazzo <daniele.varrazzo@gmail.com>

MKDIR = mkdir -p
RM = rm -f

# Customize these to select the Python to build/test
PYTHON ?= python3
PYCONFIG ?= python3-config

PYINC := $(shell $(PYCONFIG) --includes)
PYLIB := $(shell $(PYCONFIG) --ldflags) -L$(shell $(PYCONFIG) --prefix)/lib

.PHONY: build check clean

check: tests/pyrun
	pytest -v

tests/pyrun: tests/pyrun.c
	$(CC) $(PYINC) -o $@ $< $(PYLIB)

sdist:
	$(PYTHON) setup.py sdist --formats=gztar,zip

clean:
	$(RM) -r build dist tests/pyrun setproctitle.egg-info

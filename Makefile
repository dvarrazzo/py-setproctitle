# Copyright (c) 2010-2020 Daniele Varrazzo <daniele.varrazzo@gmail.com>

MKDIR = mkdir -p
RM = rm -f

# Customize these to select the Python to build/test
PYTHON ?= python3
PYCONFIG ?= python3-config

ROOT_PATH := $(shell pwd)

PYINC := $(shell $(PYCONFIG) --includes)
PYLIB := $(shell $(PYCONFIG) --ldflags) -L$(shell $(PYCONFIG) --prefix)/lib

.PHONY: build check py3 clean

build:
	$(PYTHON) py3/setup.py build

check: build tests/pyrun3
	PYTHONPATH=$(BUILD_DIR):$$PYTHONPATH \
	ROOT_PATH=$(ROOT_PATH) \
	$(PYTHON) py3/tests/setproctitle_test.py -v

tests/pyrun3: tests/pyrun.c
	$(CC) $(PYINC) -o $@ $< $(PYLIB)

sdist:
	$(PYTHON) setup.py sdist --formats=gztar,zip

clean:
	$(RM) -r py3 build dist tests/pyrun3 setproctitle.egg-info

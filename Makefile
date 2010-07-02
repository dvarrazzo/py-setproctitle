# Oh, makefile, help me with the python3 craze :D
#
# Copyright (c) 2010 Daniele Varrazzo <daniele.varrazzo@gmail.com>

MKDIR = mkdir -p
PYTHON = python
PYTHON3 = python3.1
PY2TO3 = 2to3

BUILD_DIR = build/lib.$(PYTHON)
BUILD3_DIR = build/lib.$(PYTHON3)

.PHONY: build test py3 build3 test3 clean

build:
	$(PYTHON) setup.py build --build-lib $(BUILD_DIR)

test: build
	PYTHONPATH=$(BUILD_DIR):$$PYTHONPATH \
		$(PYTHON) tests/setproctitle_test.py -v

sdist: MANIFEST
	$(PYTHON) setup.py sdist --formats=gztar,zip

MANIFEST:
	# Must run twice because the manifest contains the manifest itself.
	$(PYTHON) setup.py sdist --manifest-only
	$(PYTHON) setup.py sdist --manifest-only

py3: MANIFEST
	$(MKDIR) py3
	$(MKDIR) py3/src
	$(MKDIR) py3/tests
	for f in `cat MANIFEST`; do cp -v $$f py3/$$f; done
	$(PY2TO3) -w --no-diffs py3

build3: py3
	$(PYTHON3) py3/setup.py build --build-lib $(BUILD3_DIR)

test3: build3
	PYTHONPATH=$(BUILD3_DIR):$$PYTHONPATH \
		$(PYTHON3) py3/tests/setproctitle_test.py -v

sdist3: py3
	cd py3 && $(PYTHON3) setup.py sdist --formats=gztar,zip --dist-dir=../dist

clean:
	$(RM) -r MANIFEST py3 build dist



#!/usr/bin/env python
"""
setproctitle setup script.

Copyright (c) 2009-2020 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

import sys

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

VERSION = "1.2.2"

define_macros = {}
define_macros["SPT_VERSION"] = VERSION

if sys.platform.startswith("linux"):
    define_macros["HAVE_SYS_PRCTL_H"] = 1

elif sys.platform == "darwin":
    # __darwin__ symbol is not defined; __APPLE__ is instead.
    define_macros["__darwin__"] = 1

elif "bsd" in sys.platform:  # OMG, how many of them are?
    define_macros["BSD"] = 1
    define_macros["HAVE_SETPROCTITLE"] = 1
    define_macros["HAVE_PS_STRING"] = 1

# NOTE: the module may work on HP-UX using pstat
# thus setting define_macros['HAVE_SYS_PSTAT_H']
# see http://www.noc.utoronto.ca/~mikep/unix/HPTRICKS
# But I have none handy to test with.

mod_spt = Extension(
    "setproctitle",
    define_macros=list(define_macros.items()),
    sources=[
        "src/setproctitle.c",
        "src/spt_debug.c",
        "src/spt_setup.c",
        "src/spt_status.c",
        "src/spt_strlcpy.c",
    ],
)

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < "2.2.3":
    from distutils.dist import DistributionMetadata

    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Try to include the long description in the setup
kwargs = {}
try:
    kwargs["long_description"] = (
        open("README.rst").read() + "\n" + open("HISTORY.rst").read()
    )
    kwargs["long_description_content_type"] = "text/x-rst"
except Exception:
    pass

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: C
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Operating System :: POSIX :: Linux
Operating System :: POSIX :: BSD
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Topic :: Software Development
""".splitlines()

setup(
    name="setproctitle",
    description="A Python module to customize the process title",
    version=VERSION,
    author="Daniele Varrazzo",
    author_email="daniele.varrazzo@gmail.com",
    url="https://github.com/dvarrazzo/py-setproctitle",
    download_url="http://pypi.python.org/pypi/setproctitle/",
    license="BSD",
    platforms=["GNU/Linux", "BSD", "MacOS X", "Windows"],
    python_requires=">=3.6",
    classifiers=classifiers,
    ext_modules=[mod_spt],
    extras_require={"test": ["pytest>=6.1,<6.2"]},
    **kwargs
)

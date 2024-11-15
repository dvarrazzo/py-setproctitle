#!/usr/bin/env python
"""
setproctitle setup script.

Copyright (c) 2009-2021 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

import re
import sys

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

with open("pkg/setproctitle/__init__.py") as f:
    data = f.read()
    m = re.search(r"""(?m)^__version__\s*=\s*['"]([^'"]+)['"]""", data)
    if not m:
        raise Exception(f"cannot find version in {f.name}")
    VERSION = m.group(1)

define_macros = {}
define_macros["SPT_VERSION"] = VERSION

platform_sources = []

if sys.platform.startswith("linux"):
    define_macros["HAVE_SYS_PRCTL_H"] = 1

elif sys.platform == "darwin":
    # __darwin__ symbol is not defined; __APPLE__ is instead.
    define_macros["__darwin__"] = 1
    platform_sources.append("src/darwin_set_process_name.c")

elif "bsd" in sys.platform:  # OMG, how many of them are?
    define_macros["BSD"] = 1
    define_macros["HAVE_SETPROCTITLE"] = 1
    define_macros["HAVE_PS_STRING"] = 1

# NOTE: the module may work on HP-UX using pstat
# thus setting define_macros['HAVE_SYS_PSTAT_H']
# see http://www.noc.utoronto.ca/~mikep/unix/HPTRICKS
# But I have none handy to test with.

mod_spt = Extension(
    "setproctitle._setproctitle",
    define_macros=list(define_macros.items()),
    sources=[
        "src/setproctitle.c",
        "src/spt_debug.c",
        "src/spt_setup.c",
        "src/spt_status.c",
        "src/spt_strlcpy.c",
    ]
    + platform_sources,
)

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
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Operating System :: POSIX :: Linux
Operating System :: POSIX :: BSD
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Topic :: Software Development
""".splitlines()


class BuildError(Exception):
    pass


class setproctitle_build_ext(build_ext):
    def run(self) -> None:
        try:
            super().run()
        except Exception as e:
            print(f"Failed to build C module: {e}", file=sys.stderr)
            raise BuildError(str(e))

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            print(
                f"Failed to build extension {ext.name}: {e}", file=sys.stderr
            )
            raise BuildError(str(e))


def do_build(with_extension):
    ext_modules = [mod_spt] if with_extension else []
    setup(
        name="setproctitle",
        description="A Python module to customize the process title",
        version=VERSION,
        author="Daniele Varrazzo",
        author_email="daniele.varrazzo@gmail.com",
        url="https://github.com/dvarrazzo/py-setproctitle",
        download_url="http://pypi.python.org/pypi/setproctitle/",
        license="BSD-3-Clause",
        platforms=["GNU/Linux", "BSD", "MacOS X", "Windows"],
        python_requires=">=3.8",
        classifiers=classifiers,
        packages=["setproctitle"],
        package_dir={"setproctitle": "pkg/setproctitle"},
        ext_modules=ext_modules,
        package_data={"setproctitle": ["py.typed"]},
        extras_require={"test": ["pytest"]},
        cmdclass={"build_ext": setproctitle_build_ext},
        zip_safe=False,
        **kwargs,
    )


try:
    do_build(with_extension=True)
except BuildError:
    do_build(with_extension=False)

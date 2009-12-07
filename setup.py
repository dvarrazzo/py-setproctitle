#!/usr/bin/env python
"""
setproctitle setup script.

Copyright (c) 2009 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

VERSION = '0.3'

import os
import re
import sys
from distutils.core import setup, Extension

define_macros={}

define_macros['SPT_VERSION'] = VERSION

if sys.platform == 'linux2':
    try:
        linux_version = map(int, 
            re.search("[.0-9]+", os.popen("uname -r").read())
                .group().split(".")[:3])
    except:
        pass
    else:
        if linux_version >= [2, 6, 9]:
            define_macros['HAVE_SYS_PRCTL_H'] = 1

if sys.platform == 'darwin':
    # __darwin__ symbol is not defined; __APPLE__ is instead.
    define_macros['__darwin__'] = 1

mod_spt = Extension('setproctitle',
    define_macros=define_macros.items(),
    sources = [
        'src/setproctitle.c',
        'src/spt_status.c',
        'src/strlcpy.c', # TODO: not needed on some platform
        ])

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Try to include the long description in the setup
kwargs = {}
try: kwargs['long_description'] = open('README').read()
except: pass

setup(
    name = 'setproctitle',
    description = 'Allow customization of the process title.',
    version = VERSION,
    author = 'Daniele Varrazzo',
    author_email = 'daniele.varrazzo@gmail.com',
    url = 'http://code.google.com/p/py-setproctitle/',
    download_url = 'http://pypi.python.org/pypi/setproctitle/',
    license = 'BSD',
    platforms = ['POSIX', 'Windows'],
    classifiers = filter(None, map(str.strip, """
        Development Status :: 4 - Beta
        Intended Audience :: Developers
        License :: OSI Approved :: BSD License
        Programming Language :: C
        Programming Language :: Python
        Topic :: Software Development
        """.splitlines())),
    ext_modules = [mod_spt],
    **kwargs)

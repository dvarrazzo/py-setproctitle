#!/usr/bin/env python
"""
setproctitle setup script.

Copyright (c) 2009 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

VERSION = '0.1a0'

from distutils.core import setup, Extension

mod_spt = Extension('setproctitle',
    define_macros=[('SPT_VERSION', '"%s"' % VERSION),],
    sources = [
        'src/setproctitle.c',
        'src/spt_status.c',
        'src/strlcpy.c', # TODO: not needed on some platform
        ])

setup(
    name = 'setproctitle',
    description = 'Allow customization of the process title.',
    version = VERSION,
    author = 'Daniele Varrazzo',
    author_email = 'daniele.varrazzo@gmail.com',
    url = 'http://piro.develer.com/py-setproctitle',
    ext_modules = [mod_spt])

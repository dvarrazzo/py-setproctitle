from distutils.core import setup, Extension

mod_spt = Extension('setproctitle',
    sources = [
        'src/setproctitle.c', 
        'src/spt_status.c', 
        'src/strlcpy.c', # TODO: not needed on some platform
        ])

setup(
    name = 'setproctitle',
    description = 'Allow customization of the process title.',
    version = '0.1a0',
    author = 'Daniele Varrazzo',
    author_email = 'daniele.varrazzo@gmail.com',
    url = 'http://piro.develer.com/py-setproctitle',
    ext_modules = [mod_spt])

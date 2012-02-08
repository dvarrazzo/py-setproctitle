A ``setproctitle`` implementation for Python
============================================

:author: Daniele Varrazzo

The library allows a process to change its title (as displayed by system tools
such as ``ps`` and ``top``).

Changing the title is mostly useful in multi-process systems, for example
when a master process is forked: changing the children's title allows to
identify the task each process is busy with.  The technique is used by
PostgreSQL_ and the `OpenSSH Server`_ for example.

The procedure is hardly portable across different systems.  PostgreSQL provides
a good `multi-platform implementation`__:  this module is a Python wrapper
around PostgreSQL code.

- `Homepage <http://code.google.com/p/py-setproctitle/>`__
- `Download <http://pypi.python.org/pypi/setproctitle/>`__
- `Source repository <https://github.com/dvarrazzo/py-setproctitle>`__
- `Bug tracker <http://code.google.com/p/py-setproctitle/issues/list>`__


.. _PostgreSQL: http://www.postgresql.org
.. _OpenSSH Server: http://www.openssh.com/
.. __: http://doxygen.postgresql.org/ps__status_8c_source.html


Installation
------------

You can use ``easy_install`` to install the module: to perform a system-wide
installation use::

    sudo easy_install setproctitle

If you are an unprivileged user or you want to limit installation to a local
environment, you can use the command::

    easy_install -d /target/path setproctitle

Note that ``easy_install`` requires ``/target/path`` to be in your
``PYTHONPATH``.


Python 3 support
~~~~~~~~~~~~~~~~

As of version 1.1 the module works with Python 3.  In order to install the
module, you can use the `distribute`_ replacemente for ``easy_install``.

In order to build and test the module under Python 3, the ``Makefile``
contains some helper targets.

.. _distribute: http://pypi.python.org/pypi/distribute


Usage
-----

The ``setproctitle`` module exports the following functions:

``setproctitle(title)``
    Set *title* as the title for the current process.

``getproctitle()``
    Return the current process title.


Environment variables
~~~~~~~~~~~~~~~~~~~~~

A few environment variables can be used to customize the module behavior:

``SPT_NOENV``
    Avoid clobbering ``/proc/PID/environ``.

    On many platforms, setting the process title will clobber the
    ``environ`` memory area. ``os.environ`` will work as expected from within
    the Python process, but the content of the file ``/proc/PID/environ`` will
    be overwritten.  If you require this file not to be broken you can set the
    ``SPT_NOENV`` environment variable to any non-empty value: in this case
    the maximum length for the title will be limited to the length of the
    command line.

``SPT_DEBUG``
    Print debug information on ``stderr``.

    If the module doesn't work as expected you can set this variable to a
    non-empty value to generate information useful for debugging.  Note that
    the most useful information is printed when the module is imported, not
    when the functions are called.


Module status
-------------

The module can be currently compiled and effectively used on the following
platforms:

- GNU/Linux
- BSD
- MacOS X
- Windows

Note that on Windows there is no way to change the process string:
what the module does is to create a *Named Object* whose value can be read
using a tool such as `Process Explorer`_ (contribution of a more useful tool
to be used together with ``setproctitle`` would be well accepted).

The module can probably work on HP-UX, but I haven't found any to test with.
It is unlikely that it can work on Solaris instead.

.. _Process Explorer: http://technet.microsoft.com/en-us/sysinternals/bb896653.aspx


Other known implementations and discussions
-------------------------------------------

- `procname`_: a module exposing the same functionality, but less portable 
  and not well packaged.
- `Issue 5672`_: where the introduction of such functionality into the stdlib
  is being discussed.

.. _procname: http://code.google.com/p/procname/
.. _Issue 5672: http://bugs.python.org/issue5672


..
    vim: set filetype=rst:


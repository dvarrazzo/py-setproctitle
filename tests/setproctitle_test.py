"""setproctitle module unit test.

Use nosetests to run this test suite.

Copyright (c) 2009-2010 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

import os
import re
import sys
import shutil
import tempfile
import unittest
from subprocess import Popen, PIPE, STDOUT

from nose.plugins.skip import SkipTest

class SetproctitleTestCase(unittest.TestCase):
    def test_runner(self):
        """Test the script execution method."""
        rv = self.run_script("""
            print 10 + 20
            """)
        self.assertEqual(rv, "30\n")

    def test_init_getproctitle(self):
        """getproctitle() returns a sensible value at initial call."""
        rv = self.run_script("""
            import setproctitle
            print setproctitle.getproctitle()
            """,
            args="-u")
        self.assertEqual(rv, sys.executable + " -u\n")

    def test_setproctitle(self):
        """setproctitle() can set the process title, duh."""
        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, world!')

            import os
            print os.getpid()
            # ps can fail on kfreebsd arch
            # (http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=460331)
            print os.popen("ps -o pid,command 2> /dev/null").read()
            """)
        lines = filter(None, rv.splitlines())
        pid = lines.pop(0)
        pids = dict([r.strip().split(None, 1) for r in lines])

        title = self._clean_up_title(pids[pid])
        self.assertEqual(title, "Hello, world!")

    def test_prctl(self):
        """Check that prctl is called on supported platforms."""
        linux_version = []
        if sys.platform == 'linux2':
            try:
                linux_version = map(int,
                    re.search("[.0-9]+", os.popen("uname -r").read())
                        .group().split(".")[:3])
            except:
                pass

        if linux_version < [2,6,9]:
            raise SkipTest

        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, prctl!')
            print open('/proc/self/status').read()
            """)
        status = dict([r.split(':', 1) for r in rv.splitlines() if ':' in r])
        self.assertEqual(status['Name'].strip(), "Hello, prctl!")

    def test_getproctitle(self):
        """getproctitle() can read the process title back."""
        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, world!')
            print setproctitle.getproctitle()
            """)
        self.assertEqual(rv, "Hello, world!\n")

    def test_environ(self):
        """Check that clobbering environ didn't break env."""
        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, world! ' + 'X' * 1024)

            # set a new env variable, update another one
            import os
            os.environ['TEST_SETENV'] = "setenv-value"
            os.environ['PATH'] = os.environ.get('PATH', '') \
                    + os.pathsep + "fakepath"

            # read the environment from a spawned process inheriting the
            # updated env
            newenv = dict([r.split("=",1)
                    for r in os.popen("env").read().splitlines()
                    if '=' in r])

            print setproctitle.getproctitle()
            print newenv['TEST_SETENV']
            print newenv['PATH']
            """)

        title, test, path = rv.splitlines()
        self.assert_(title.startswith("Hello, world! XXXXX"), title)
        self.assertEqual(test, 'setenv-value')
        self.assert_(path.endswith('fakepath'), path)

    def test_issue_8(self):
        """Test that the module works with 'python -m'."""
        module = 'spt_issue_8'
        pypath = os.environ.get('PYTHONPATH', None)
        dir = tempfile.mkdtemp()
        os.environ['PYTHONPATH'] = dir + os.pathsep + (pypath or '')
        try:
            open(dir + '/' + module + '.py', 'w').write(
                self._clean_whitespaces(r"""
                    import setproctitle
                    setproctitle.setproctitle("Hello, module!")

                    import os
                    print os.getpid()
                    print os.popen("ps -o pid,command 2> /dev/null").read()
                """))

            rv = self.run_script(args="-m " + module)
            lines = filter(None, rv.splitlines())
            pid = lines.pop(0)
            pids = dict([r.strip().split(None, 1) for r in lines])

            title = self._clean_up_title(pids[pid])
            self.assertEqual(title, "Hello, module!")

        finally:
            shutil.rmtree(dir, ignore_errors=True)
            if pypath is not None:
                os.environ['PYTHONPATH'] = pypath
            else:
                del os.environ['PYTHONPATH']


    def run_script(self, script=None, args=None):
        """run a script in a separate process.

        if the script completes successfully, return the concatenation of
        ``stdout`` and ``stderr``. else fail.
        """
        cmdline = sys.executable
        if args:
            cmdline = cmdline + " " + args

        proc = Popen(cmdline,
                stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                shell=True, close_fds=True)

        if script is not None:
            script = self._clean_whitespaces(script)

        out = proc.communicate(script)[0]
        if 0 != proc.returncode:
            print out
            self.fail("test script failed")

        return out

    def _clean_whitespaces(self, script):
        """clean up a script in a string

        Remove the amount of whitelines found in the first nonblank line
        """
        script = script.splitlines(True)
        while script and script[0].isspace():
            script.pop(0)

        if not script:
            raise ValueError("empty script")

        line1 = script[0]
        spaces = script[0][:-len(script[0].lstrip())]
        assert spaces.isspace()

        for i, line in enumerate(script):
            if line.isspace(): continue
            if line.find(spaces) != 0:
                raise ValueError("inconsistent spaces at line %d (%s)"
                        % (i + 1, line.strip()))
            script[i] = line[len(spaces):]

        # drop final blank lines: they produce import errors
        while script and script[-1].isspace():
            del script[-1]

        assert not script[0][0].isspace(), script[0]
        return ''.join(script)

    def _clean_up_title(self, title):
        """Clean up a string from the prefix added by the platform.
        """
        # BSD's setproctitle decorates the title with the process name.
        if 'bsd' in sys.platform:
            procname = os.path.basename(sys.executable)
            title = ' '.join([t for t in title.split(' ')
                if procname not in t])  

        return title


if __name__ == '__main__':
    unittest.main()

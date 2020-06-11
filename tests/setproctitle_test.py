"""setproctitle module unit test.

Use pytest to run this test suite.

The tests are executed in external processes: setproctitle should
never be imported directly from here.

Copyright (c) 2009-2020 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

import os
import re
import sys
import subprocess as sp

import pytest

IS_PYPY = "__pypy__" in sys.builtin_module_names


@pytest.fixture(scope="session")
def pyrun(pyconfig):
    """
    Build the pyrun executable and return its path
    """
    # poor man's make
    here = os.path.abspath(os.path.dirname(__file__))
    ver2 = "%s.%s" % sys.version_info[:2]
    source = os.path.join(here, "pyrun.c")
    target = os.path.join(here, f"pyrun{ver2}")
    if (
        os.path.exists(target)
        and os.stat(target).st_mtime > os.stat(source).st_mtime
    ):
        return target

    cmdline = ["cc"]  # big punt
    cmdline.extend(pyconfig("includes"))
    cmdline.extend(["-o", target, source])
    cmdline.extend(pyconfig("ldflags"))
    cmdline.append(f"-L{pyconfig('prefix')[0]}/lib")
    sp.check_call(cmdline)
    return target


@pytest.fixture(scope="session")
def pyconfig():
    """Return the result of 'python-config --opt' as a list of strings"""
    pyexe = os.path.realpath(sys.executable)
    ver2 = "%s.%s" % sys.version_info[:2]
    for name in (f"python{ver2}-config", "python3-config", "python-config"):
        pyconfexe = os.path.join(os.path.dirname(pyexe), name)
        if os.path.exists(pyconfexe):
            break
    else:
        pytest.fail(
            f"can't find python-config from executable {sys.executable}"
        )

    # Travis' Python 3.8 is not built with --embed
    help = sp.check_output([pyconfexe, "--help"])
    has_embed = b"--embed" in help

    def pyconfig_func(opt):
        cmdline = [pyconfexe, f"--{opt}"]
        if has_embed:
            cmdline.append("--embed")
        bout = sp.check_output(cmdline)
        out = bout.decode(
            sys.getfilesystemencoding()  # sounds like a good bet
        )
        return out.split()

    return pyconfig_func


@pytest.fixture(scope="session")
def spt_directory():
    """
    Where is the setproctitle module installed?
    """
    rv = run_script(
        """
import os
import setproctitle
print(os.path.dirname(setproctitle.__file__))
"""
    )
    return rv.rstrip()


def test_runner():
    """Test the script execution method."""
    rv = run_script(
        """
print(10 + 20)
"""
    )
    assert rv == "30\n"


def test_no_import_side_effect():
    """
    Check that importing the module doesn't cause side effects.
    """
    rv = run_script(
        """
import os

def print_stuff():
    for fn in "cmdline status comm".split():
        if os.path.exists(f"/proc/self/{fn}"):
            with open(f"/proc/self/{fn}") as f:
                print(f.readline().rstrip())

print_stuff()
print("---")
import setproctitle
print_stuff()
"""
    )
    before, after = rv.split("---\n")
    assert before == after


def test_init_getproctitle():
    """getproctitle() returns a sensible value at initial call."""
    rv = run_script(
        """
import setproctitle
print(setproctitle.getproctitle())
""",
        args="-u",
    )
    assert rv == sys.executable + " -u\n"


def test_setproctitle():
    """setproctitle() can set the process title, duh."""
    rv = run_script(
        r"""
import setproctitle
setproctitle.setproctitle('Hello, world!')

import os
print(os.getpid())
# ps can fail on kfreebsd arch
# (http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=460331)
print(os.popen("ps -x -o pid,command 2> /dev/null").read())
"""
    )
    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])
    title = _clean_up_title(pids[pid])
    assert title == "Hello, world!"


def test_prctl():
    """Check that prctl is called on supported platforms."""
    linux_version = []
    if sys.platform in ("linux", "linux2"):
        try:
            f = os.popen("uname -r")
            name = f.read()
            f.close()
        except Exception:
            pass
        else:
            linux_version = list(
                map(int, re.search("[.0-9]+", name).group().split(".")[:3])
            )

    if linux_version < [2, 6, 9]:
        pytest.skip("syscall not supported")

    rv = run_script(
        r"""
import setproctitle
setproctitle.setproctitle('Hello, prctl!')
print(open('/proc/self/status').read())
"""
    )
    status = dict([r.split(":", 1) for r in rv.splitlines() if ":" in r])
    assert status["Name"].strip() == "Hello, prctl!"


def test_getproctitle():
    """getproctitle() can read the process title back."""
    rv = run_script(
        r"""
import setproctitle
setproctitle.setproctitle('Hello, world!')
print(setproctitle.getproctitle())
"""
    )
    assert rv == "Hello, world!\n"


def test_kwarg():
    """setproctitle() supports keyword args."""
    rv = run_script(
        r"""
import setproctitle
setproctitle.setproctitle(title='Hello, world!')
print(setproctitle.getproctitle())
"""
    )
    assert rv == "Hello, world!\n"


def test_environ():
    """Check that clobbering environ didn't break env."""
    rv = run_script(
        r"""
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

print(setproctitle.getproctitle())
print(newenv['TEST_SETENV'])
print(newenv['PATH'])
"""
    )

    title, test, path = rv.splitlines()
    assert title.startswith("Hello, world! XXXXX"), title
    assert test == "setenv-value"
    assert path.endswith("fakepath"), path


def test_issue_8(monkeypatch, tmp_path):
    """Test that the module works with 'python -m'."""
    module = "spt_issue_8"
    monkeypatch.setenv(
        "PYTHONPATH",
        str(tmp_path) + os.pathsep + os.environ.get("PYTHONPATH", ""),
    )

    with open(tmp_path / f"{module}.py", "w") as f:
        f.write(
            r"""
import setproctitle
setproctitle.setproctitle("Hello, module!")

import os
print(os.getpid())
print(os.popen("ps -x -o pid,command 2> /dev/null").read())
            """
        )

    rv = run_script(args="-m " + module)
    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])

    title = _clean_up_title(pids[pid])
    assert title == "Hello, module!"


def test_unicode():
    """Title can contain unicode characters."""
    snowman = "\u2603"
    try:
        snowman.encode(sys.getdefaultencoding())
    except UnicodeEncodeError:
        pytest.skip(
            "default encoding '%s' can't deal with snowmen"
            % sys.getdefaultencoding()
        )

    try:
        snowman.encode(sys.getfilesystemencoding())
    except UnicodeEncodeError:
        pytest.skip(
            "file system encoding '%s' can't deal with snowmen"
            % sys.getfilesystemencoding()
        )

    rv = run_script(
        r"""
snowman = u'\u2603'

import setproctitle
setproctitle.setproctitle("Hello, " + snowman + "!")

import os
import locale
from subprocess import Popen, PIPE
print(os.getpid())
proc = Popen("ps -x -o pid,command 2> /dev/null", shell=True,
    close_fds=True, stdout=PIPE, stderr=PIPE)
buf = proc.stdout.read()
print(buf.decode(locale.getpreferredencoding(), 'replace'))
"""
    )
    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])

    snowmen = [
        "\u2603",  # ps supports unicode
        r"\M-b\M^X\M^C",  # ps output on BSD
        r"M-bM^XM^C",  # ps output on some Darwin < 11.2
        "\ufffdM^XM^C",  # ps output on Darwin 11.2
    ]
    title = _clean_up_title(pids[pid])
    for snowman in snowmen:
        if title == "Hello, " + snowman + "!":
            break
    else:
        pytest.fail("unexpected ps output: %r" % title)


def test_weird_args():
    """No problem with encoded arguments."""
    euro = "\u20ac"
    snowman = "\u2603"
    try:
        rv = run_script(
            r"""
import setproctitle
setproctitle.setproctitle("Hello, weird args!")

import os
print(os.getpid())
print(os.popen("ps -x -o pid,command 2> /dev/null").read())
""",
            args=" ".join(["-", "hello", euro, snowman]),
        )
    except TypeError:
        pytest.skip("apparently we can't pass unicode args to a program")

    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])

    title = _clean_up_title(pids[pid])
    assert title == "Hello, weird args!"


def test_weird_path(tmp_path, spt_directory):
    """No problem with encoded argv[0] path."""
    _check_4388()
    euro = "\u20ac"
    snowman = "\u2603"
    dir = tmp_path / euro / snowman
    try:
        os.makedirs(dir)
    except UnicodeEncodeError:
        pytest.skip("file system doesn't support unicode")

    exc = dir / "python"
    os.symlink(sys.executable, exc)

    rv = run_script(
        f"""
import sys
sys.path.insert(0, {repr(spt_directory)})

import setproctitle
setproctitle.setproctitle("Hello, weird path!")

import os
print(os.getpid())
print(os.popen("ps -x -o pid,command 2> /dev/null").read())
""",
        args=" ".join(["-", "foo", "bar", "baz"]),
        executable=exc,
    )
    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])

    title = _clean_up_title(pids[pid])
    assert title == "Hello, weird path!"


def test_embedded(pyrun):
    """Check the module works with embedded Python.
    """
    if IS_PYPY:
        pytest.skip("skip test, pypy")

    if not os.path.exists("/proc/%s/cmdline" % os.getpid()):
        pytest.skip("known failure: '/proc/PID/cmdline' not available")

    rv = run_script(
        r"""
import setproctitle
setproctitle.setproctitle("Hello, embedded!")

import os
print(os.getpid())
print(os.popen("ps -x -o pid,command 2> /dev/null").read())
""",
        executable=pyrun,
    )
    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])

    title = _clean_up_title(pids[pid])
    assert title == "Hello, embedded!"


def test_embedded_many_args(pyrun):
    """Check more complex cmdlines are handled in embedded env too."""
    if IS_PYPY:
        pytest.skip("skip test, pypy")

    if not os.path.exists("/proc/%s/cmdline" % os.getpid()):
        pytest.skip("known failure: '/proc/PID/cmdline' not available")

    rv = run_script(
        r"""
import setproctitle
setproctitle.setproctitle("Hello, embedded!")

import os
print(os.getpid())
print(os.popen("ps -x -o pid,command 2> /dev/null").read())
""",
        executable=pyrun,
        args=" ".join(["foo", "bar", "baz"]),
    )
    lines = [line for line in rv.splitlines() if line]
    pid = lines.pop(0)
    pids = dict([r.strip().split(None, 1) for r in lines])

    title = _clean_up_title(pids[pid])
    assert title == "Hello, embedded!"


def test_noenv():
    """Check that SPT_NOENV avoids clobbering environ."""
    if not os.path.exists("/proc/self/environ"):
        pytest.skip("'/proc/self/environ' not available")

    env = os.environ.copy()
    env["SPT_TESTENV"] = "testenv"
    rv = run_script(
        """
import os
os.environ['SPT_NOENV'] = "1"

cmdline_len = len(open('/proc/self/cmdline').read())
print(cmdline_len)
print('SPT_TESTENV=testenv' in open('/proc/self/environ').read())

import setproctitle
setproctitle.setproctitle('X' * cmdline_len * 10)

title = open('/proc/self/cmdline').read().rstrip()
print(title)
print(len(title))

print('SPT_TESTENV=testenv' in open('/proc/self/environ').read())
    """,
        env=env,
    )
    lines = rv.splitlines()
    cmdline_len = int(lines[0])
    assert lines[1] == "True", "can't verify testenv"
    title = lines[2]
    assert "XXX" in _clean_up_title(title), "title not set as expected"
    title_len = int(lines[3])
    assert lines[4] == "True", "env has been clobbered"
    assert (
        title_len <= cmdline_len
    ), "title (len %s) not limited to argv (len %s)" % (title_len, cmdline_len)


# Support functions


def run_script(script=None, args=None, executable=None, env=None):
    """run a script in a separate process.

    if the script completes successfully, return its ``stdout``,
    else fail the test.
    """
    if executable is None:
        executable = sys.executable

    cmdline = str(executable)
    if args:
        cmdline = cmdline + " " + args

    proc = sp.Popen(
        cmdline,
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        env=env,
        shell=True,
        close_fds=True,
    )

    out, err = proc.communicate(script and script.encode())
    if 0 != proc.returncode:
        print(out)
        print(err)
        pytest.fail("test script failed")

    # Py3 subprocess generates bytes strings.
    out = out.decode()

    return out


def _clean_up_title(title):
    """Clean up a string from the prefix added by the platform.
    """
    # BSD's setproctitle decorates the title with the process name.
    if "bsd" in sys.platform:
        procname = os.path.basename(sys.executable)
        title = " ".join([t for t in title.split(" ") if procname not in t])

    return title


def _check_4388():
    """Check if the system is affected by bug #4388.

    If positive, unicode chars in the cmdline are not reliable,
    so bail out.

    see: http://bugs.python.org/issue4388
    """
    if sys.getfilesystemencoding() == "ascii":
        # in this case the char below would get translated in some
        # inconsistent way.
        # I'm not getting why the FS encoding is involved in process
        # spawning, the whole story just seems a gigantic can of worms.
        return

    p = sp.Popen([sys.executable, "-c", "ord('\xe9')"], stderr=sp.PIPE)
    p.communicate()
    if p.returncode:
        pytest.skip("bug #4388 detected")

import os
import sys
import subprocess as sp

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "embedded: the test create an embedded executable"
    )


skip_if_win32 = pytest.mark.skipif(
    "sys.platform == 'win32'", reason="skipping Posix tests on Windows"
)

skip_if_macos = pytest.mark.skipif(
    "sys.platform == 'darwin'", reason="skipping test on macOS"
)

skip_if_pypy = pytest.mark.skipif(
    "'__pypy__' in sys.builtin_module_names", reason="skipping test on pypy"
)

skip_if_no_proc_env = pytest.mark.skipif(
    "not os.path.exists('/proc/self/environ')",
    reason="'/proc/self/environ' not available",
)

skip_if_no_proc_cmdline = pytest.mark.skipif(
    "not os.path.exists('/proc/%s/cmdline' % os.getpid())",
    reason="'/proc/PID/cmdline' not available",
)

skip_if_no_proc_tasks = pytest.mark.skipif(
    "not os.path.exists('/proc/self/task')",
    reason="'/proc/self/task' not available",
)


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
print(os.path.dirname(os.path.dirname(setproctitle.__file__)))
"""
    )
    return rv.rstrip()


@pytest.fixture(scope="function")
def tmp_pypath(monkeypatch, tmp_path):
    """
    return a tmp directory which has been added to the python path
    """
    monkeypatch.setenv(
        "PYTHONPATH",
        str(tmp_path) + os.pathsep + os.environ.get("PYTHONPATH", ""),
    )
    return tmp_path


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
        if out:
            print(out.decode("utf8", "replace"), file=sys.stdout)
        if err:
            print(err.decode("utf8", "replace"), file=sys.stderr)
        pytest.fail("test script failed")

    # Py3 subprocess generates bytes strings.
    out = out.decode()

    return out

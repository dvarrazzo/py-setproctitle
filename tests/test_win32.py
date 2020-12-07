import pytest
import setproctitle
import sys

if sys.platform != 'win32':
    pytest.skip("skipping Windows tests",
                allow_module_level=True)


def test_setproctitle():
    title = "setproctitle_test"
    setproctitle.setproctitle(title)
    assert title == setproctitle.getproctitle()

def test_setthreadtitle():
    title = "setproctitle_test"
    # This is currently a no-op on Windows. Let's make sure
    # that at least it doesn't error out.
    setproctitle.setthreadtitle(title)

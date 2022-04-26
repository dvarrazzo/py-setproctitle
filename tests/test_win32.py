import pytest
import setproctitle
import sys  # noqa

skip_if_not_win32 = pytest.mark.skipif(
    "sys.platform != 'win32'", reason="Windows only test"
)

pytestmark = [skip_if_not_win32]


def test_setproctitle():
    title = "setproctitle_test"
    setproctitle.setproctitle(title)
    assert title == setproctitle.getproctitle()


def test_setthreadtitle():
    title = "setproctitle_test"
    # This is currently a no-op on Windows. Let's make sure
    # that at least it doesn't error out.
    setproctitle.setthreadtitle(title)

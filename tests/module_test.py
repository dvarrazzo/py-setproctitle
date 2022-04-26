from .conftest import run_script, skip_if_win32


@skip_if_win32
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


def test_version():
    """Test that the module has a version"""
    rv = run_script(
        """
import setproctitle
print(setproctitle.__version__)
"""
    )
    assert rv


def test_c_extension_built():
    """Test that the C extension was built"""
    rv = run_script(
        """
from setproctitle import _setproctitle
"""
    )
    assert rv == ""

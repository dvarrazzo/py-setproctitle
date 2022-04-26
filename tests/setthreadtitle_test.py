import os  # noqa
import sys  # noqa

from .conftest import run_script, skip_if_win32, skip_if_no_proc_tasks

pytestmark = [skip_if_win32, skip_if_no_proc_tasks]


def test_thread_title_unchanged():
    rv = run_script(
        """
from glob import glob

def print_stuff():
    for fn in sorted(glob("/proc/self/task/*/comm")):
        with open(fn) as f:
            print(f.readline().rstrip())

print_stuff()
print("---")
import setproctitle
print_stuff()
print("---")
print(setproctitle.getthreadtitle())
"""
    )
    before, after, gtt = rv.split("---\n")
    assert before == after
    assert before == gtt


def test_set_thread_title():
    run_script(
        """
from glob import glob
import setproctitle
setproctitle.setthreadtitle("hello" * 10)

(fn,) = glob("/proc/self/task/*/comm")
with open(fn) as f:
    assert f.read().rstrip() == "hello" * 3
"""
    )


def test_set_threads_title():
    run_script(
        """
import time
import threading
from glob import glob

(fn,) = glob("/proc/self/task/*/comm")
with open(fn) as f:
    orig = f.read().rstrip()

import setproctitle

def worker(title):
    setproctitle.setthreadtitle(title)
    while 1:
        time.sleep(1)

t1 = threading.Thread(target=worker, args=('reader',), daemon=True)
t2 = threading.Thread(target=worker, args=('writer',), daemon=True)
t1.start()
t2.start()

comms = []
for fn in glob("/proc/self/task/*/comm"):
    with open(fn) as f:
        comms.append(f.read().rstrip())

comms.sort()
assert comms == sorted([orig, "reader", "writer"])
"""
    )

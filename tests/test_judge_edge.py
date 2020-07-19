"""
This test batch makes sure that the judge handles 'edge cases' well (either malicious attempts to break the
system, or some unintended thing like a huge amount of data sent to stdout).
"""

import sys
sys.path.append('./')

from judge_submission import judge_submission
from env_vars import *
from redis import Redis
from rq import Queue
from shutil import copyfile
import tempfile
import pytest

q = Queue(is_async=False, connection=Redis())


@pytest.fixture
def tempdir():
    tempdir = tempfile.mkdtemp(prefix='judge-')
    yield tempdir


def test_compiler_bomb(tempdir):
    """Make sure the judge is not vulnerable to a compiler bomb (size of error output)."""
    copyfile('./sample_problem_info/test/solutions/compilerbomb.cpp', tempdir + '/compilerbomb.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'compilerbomb.cpp', 'cpp'))
    assert job.result['status'] == 'compile_error' and len(job.result['compile_error']) < COMPILE_ERROR_OUTPUT + 256


def test_runtime_bomb(tempdir):
    """Make sure the judge is not vulnerable to a runtime bomb (size of code output)."""
    copyfile('./sample_problem_info/test/solutions/runtimebomb.py', tempdir + '/runtimebomb.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'runtimebomb.py', 'python'))
    assert job.result['subtasks'][0][0][0] == 'MLE'

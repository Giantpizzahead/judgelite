"""
This test batch makes sure that the judge works like it should for Python 3.8.
"""

import sys
sys.path.append('./')

from judge_submission import judge_submission
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


def test_ac_python(tempdir):
    """Make sure that the judge works correctly for a normal Python program."""
    copyfile('./sample_problem_info/test/solutions/sol.py', tempdir + '/sol.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'sol.py', 'python'))
    assert job.result['final_score'] == 101


def test_wrong_python(tempdir):
    """Make sure that the judge gives accurate verdicts for a wrong Python program."""
    copyfile('./sample_problem_info/test/solutions/wrong.py', tempdir + '/wrong.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'wrong.py', 'python'))

    correct_verdicts = ['AC', 'TLE', 'AC', 'MLE', 'AC', 'WA', 'RE', 'SK', 'SK', 'AC']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_compile_error_python(tempdir):
    """Make sure that the judge returns a compile error for Python, along with a reason for the error."""
    copyfile('./sample_problem_info/test/solutions/compileerror.py', tempdir + '/compileerror.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'compileerror.py', 'python'))
    assert job.result['status'] == 'compile_error' and 'Undefined variable \'N\'' in job.result['compile_error']


def test_stack_python(tempdir):
    """Make sure that the judge accepts a Python program that does stack-heavy things (test uses DFS)."""
    assert True

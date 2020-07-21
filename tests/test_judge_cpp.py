"""
This test batch makes sure that the judge works like it should for C++ 17.
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


def test_ac_cpp(tempdir):
    """Make sure that the judge works correctly for a correct C++ program."""
    copyfile('./sample_problem_info/test/solutions/sol.cpp', tempdir + '/sol.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'sol.cpp', 'cpp'))
    assert job.result['final_score'] == 101


def test_wrong_cpp(tempdir):
    """Make sure that the judge gives accurate verdicts for a wrong C++ program."""
    copyfile('./sample_problem_info/test/solutions/wrong.cpp', tempdir + '/wrong.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'wrong.cpp', 'cpp'))

    correct_verdicts = ['AC', 'RE', 'AC', 'MLE', 'WA', 'AC', 'TLE', 'SK', 'SK', 'AC']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_compile_error_cpp(tempdir):
    """Make sure that the judge returns a compile error for C++, along with a reason for the error."""
    copyfile('./sample_problem_info/test/solutions/compileerror.cpp', tempdir + '/compileerror.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'compileerror.cpp', 'cpp'))
    assert job.result['status'] == 'compile_error' and 'error: \'N\' was not declared' in job.result['compile_error']


def test_stack_cpp(tempdir):
    """Make sure that the judge accepts a C++ program that does stack-heavy things (test uses DFS)."""
    copyfile('./sample_problem_info/test4/solutions/lca.cpp', tempdir + '/lca.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test4', 'lca.cpp', 'cpp'))
    assert job.result['final_score'] == 42

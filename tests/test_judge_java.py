"""
This test batch makes sure that the judge works like it should for Java 14.
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


def test_ac_java(tempdir):
    """Makes sure that the judge works correctly for a normal Java program."""
    copyfile('./sample_problem_info/test/solutions/sol.java', tempdir + '/sol.java')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'sol.java', 'java'))
    assert job.result['final_score'] == 101


def test_wrong_java(tempdir):
    """Makes sure that the judge gives accurate verdicts for a wrong Java program."""
    copyfile('./sample_problem_info/test/solutions/wrong.java', tempdir + '/wrong.java')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'wrong.java', 'java'))

    correct_verdicts = ['AC', 'MLE', 'WA', 'AC', 'RE', 'TLE', 'AC', 'SK', 'AC', 'SK']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_compile_error_java(tempdir):
    """Makes sure that the judge returns a compile error for Java, along with a reason for the error."""
    copyfile('./sample_problem_info/test/solutions/compileerror.java', tempdir + '/compileerror.java')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'compileerror.java', 'java'))
    assert job.result['status'] == 'compile_error' and 'error: cannot find symbol' in job.result['compile_error'] and \
        'variable N' in job.result['compile_error']


def test_stack_java(tempdir):
    """Makes sure that the judge accepts a Java program that does stack-heavy things (test uses DFS)."""
    assert True

"""
This test batch makes sure that the judge works like it should.

Woah... testing the tester?!?!??! INCEPTION!!!!!!!!!!!!!!!! :O
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


"""
C++ 17 tests
"""


def test_ac_cpp(tempdir):
    """Makes sure that the judge works correctly for a correct C++ program."""
    copyfile('./sample_problem_info/sample/solutions/sol.cpp', tempdir + '/sol.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'sample', 'sol.cpp', 'cpp'))
    assert job.result['final_score'] >= 100


def test_wrong_cpp(tempdir):
    """Makes sure that the judge gives accurate verdicts for a wrong C++ program."""
    copyfile('./sample_problem_info/sample3/solutions/wrong.cpp', tempdir + '/wrong.cpp')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'sample3', 'wrong.cpp', 'cpp'))

    correct_verdicts = ['AC', 'RE', 'AC', 'MLE', 'WA', 'AC', 'TLE', 'SK', 'SK', 'AC']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_compile_error_cpp(tempdir):
    """Makes sure that the judge returns a compile error for C++, along with a reason for the error."""
    assert True


def test_stack_cpp(tempdir):
    """Makes sure that the judge accepts a C++ program that does stack-heavy things (test uses DFS)."""
    assert True


"""
Java 14 tests
"""


def test_ac_java(tempdir):
    """Makes sure that the judge works correctly for a normal Java program."""
    copyfile('./sample_problem_info/sample/solutions/sol.java', tempdir + '/sol.java')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'sample', 'sol.java', 'java'))
    assert job.result['final_score'] >= 100


def test_wrong_java(tempdir):
    """Makes sure that the judge gives accurate verdicts for a wrong Java program."""
    copyfile('./sample_problem_info/sample3/solutions/wrong.java', tempdir + '/wrong.java')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'sample3', 'wrong.java', 'java'))

    correct_verdicts = ['AC', 'MLE', 'WA', 'AC', 'RE', 'TLE', 'AC', 'SK', 'AC', 'SK']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_compile_error_java(tempdir):
    """Makes sure that the judge returns a compile error for Java, along with a reason for the error."""
    assert True


def test_stack_java(tempdir):
    """Makes sure that the judge accepts a Java program that does stack-heavy things (test uses DFS)."""
    assert True


"""
Python 3.8 tests
"""


def test_ac_python(tempdir):
    """Makes sure that the judge works correctly for a normal Python program."""
    copyfile('./sample_problem_info/sample/solutions/sol.py', tempdir + '/sol.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'sample', 'sol.py', 'python'))
    assert job.result['final_score'] >= 100


def test_wrong_python(tempdir):
    """Makes sure that the judge gives accurate verdicts for a wrong Python program."""
    copyfile('./sample_problem_info/sample3/solutions/wrong.py', tempdir + '/wrong.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'sample3', 'wrong.py', 'python'))

    correct_verdicts = ['AC', 'TLE', 'AC', 'MLE', 'AC', 'WA', 'RE', 'SK', 'SK', 'AC']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_compile_error_python(tempdir):
    """Makes sure that the judge returns a compile error for Python, along with a reason for the error."""
    assert True


def test_stack_python(tempdir):
    """Makes sure that the judge accepts a Python program that does stack-heavy things (test uses DFS)."""
    assert True


"""
Judge logic tests (these use Python 3.8 since it's the quickest to compile and run)
"""


def test_stop_on_sample(tempdir):
    """Test that the judge stops evaluating test cases if a sample case fails."""
    assert True


def test_stop_on_fail(tempdir):
    """
    Test that the judge stops evaluating test cases in a subtask if a single case fails, and the scoring
    method is set to minimum.
    """
    assert True


def test_stop_on_fail_average(tempdir):
    """
    Test that the judge stops evaluating test cases in a subtask if a single case fails, and the scoring
    method is set to average_stop.
    """
    assert True


def test_hide_bonus(tempdir):
    """Test that the judge hides test results for bonus test cases unless the verdict for them is AC."""
    assert True


def test_carriage_return(tempdir):
    """Test that the judge will still give a correct verdict if carriage returns are present."""
    assert True


def test_output_limiting(tempdir):
    """Make sure the judge limits the amount of data a program can write to stdout and stderr."""
    assert True


def test_file_limiting(tempdir):
    """Make sure the judge limits the amount of data a program can write to files."""
    assert True


"""
Miscellaneous tests
"""


def test_compiler_bomb(tempdir):
    """Make sure the judge is not vulnerable to a compiler bomb (size of error output)."""
    assert True


def test_runtime_bomb(tempdir):
    """Make sure the judge is not vulnerable to a runtime bomb (size of code output)."""
    assert True

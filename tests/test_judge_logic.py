"""
This test batch makes sure that the judge's logic works as expected. It uses Python 3.8 as the test language,
since that's the fastest one to compile and run.
"""

import sys
sys.path.append('./')

from env_vars import *
from judge_submission import judge_submission
from redis import Redis
from rq import Queue
from shutil import copyfile
from os.path import isfile
import re
import tempfile
import pytest

q = Queue(is_async=False, connection=Redis())


@pytest.fixture
def tempdir():
    tempdir = tempfile.mkdtemp(prefix='judge-')
    yield tempdir


def test_stop_on_sample(tempdir):
    """Test that the judge stops evaluating test cases if a sample case fails."""
    copyfile('./sample_problem_info/test/solutions/stop_on_sample.py', tempdir + '/stop_on_sample.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'stop_on_sample.py', 'python', 'username'))
    assert job.result['final_score'] == 0


def test_stop_on_fail_average(tempdir):
    """
    Test that the judge stops evaluating test cases in a subtask if a single case fails, and the scoring
    method is set to average_stop.
    """
    copyfile('./sample_problem_info/test2/solutions/wrong.py', tempdir + '/wrong.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test2', 'wrong.py', 'python', 'username'))

    correct_verdicts = ['AC', 'WA', 'SK', 'AC', 'WA', 'SK', 'AC', 'SK', 'SK']
    judge_verdicts = []
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][2][i][0])
    assert correct_verdicts == judge_verdicts


def test_stop_on_fail(tempdir):
    """
    Test that the judge stops evaluating test cases in a subtask if a single case fails, and the scoring
    method is set to minimum.
    """
    copyfile('./sample_problem_info/test3/solutions/wrong.py', tempdir + '/wrong.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test3', 'wrong.py', 'python', 'username'))
    assert job.result['subtasks'][0][1][0] == 'SK' and job.result['subtasks'][2][3][0] == 'SK' \
        and job.result['final_score'] == 5


def test_depends_on(tempdir):
    """Test that the 'depends_on' setting works as expected."""
    copyfile('./sample_problem_info/test3/solutions/depends_on.py', tempdir + '/depends_on.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test3', 'depends_on.py', 'python', 'username'))

    correct_subtask_verdicts = ['AC', 'WA', 'AC', 'AC', 'SK', 'AC', 'SK', 'WA', 'SK', 'SK', 'WA', 'AC', 'SK']
    judge_subtask_verdicts = []
    for i in range(13):
        judge_subtask_verdicts.append(job.result['subtasks'][i][0][0])
    assert correct_subtask_verdicts == judge_subtask_verdicts


def test_carriage_return(tempdir):
    """Test that the judge will still give a correct verdict if carriage returns are present."""
    copyfile('./sample_problem_info/test/solutions/carriage_return.py', tempdir + '/carriage_return.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'carriage_return.py', 'python', 'username'))

    correct_verdicts = ['AC', 'AC', 'WA', 'WA', 'AC', 'AC', 'WA', 'SK', 'SK', 'SK']
    judge_verdicts = []
    for i in range(7):
        judge_verdicts.append(job.result['subtasks'][0][i][0])
    for i in range(3):
        judge_verdicts.append(job.result['subtasks'][1][i][0])
    assert correct_verdicts == judge_verdicts


def test_output_limiting(tempdir, capsys):
    """Make sure the judge limits the amount of data a program can write to stdout and stderr."""
    copyfile('./sample_problem_info/test4/solutions/output_dump.py', tempdir + '/output_dump.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test4', 'output_dump.py', 'python', 'username'))
    assert not job.is_failed

    # Make sure all file sizes are small
    captured = capsys.readouterr()
    truncated_amount = re.findall('\[([0-9.]+) MB truncated\]', captured.err)
    for amount in truncated_amount:
        x = float(amount)
        assert x <= MAX_OUTPUT_SIZE + 0.1


def test_file_limiting(tempdir, capsys):
    """Make sure the judge limits the amount of data a program can write to files."""
    copyfile('./sample_problem_info/test4/solutions/file_dump.py', tempdir + '/file_dump.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test4', 'file_dump.py', 'python', 'username'))

    # Make sure all file sizes are small
    captured = capsys.readouterr()
    truncated_amount = re.findall('\[([0-9.]+) MB truncated\]', captured.err)
    for amount in truncated_amount:
        x = float(amount)
        assert x <= MAX_OUTPUT_SIZE + 0.1


def test_fill_missing_output(tempdir):
    """
    Make sure that the judge generates output files using the submitted program if the
    fill_missing_output setting is true. Also makes sure that minimum stops the program early.
    """
    copyfile('./sample_problem_info/test5/solutions/sol.py', tempdir + '/sol.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test5', 'sol.py', 'python', 'username'))
    assert isfile('./sample_problem_info/test5/subtasks/main/01.out') and \
        not isfile('./sample_problem_info/test5/subtasks/main/03.out') and job.result['final_score'] == 0

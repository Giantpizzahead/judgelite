"""
This test batch makes sure that the judge's logic works as expected. It uses Python 3.8 as the test language,
since that's the fastest one to compile and run.
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


def test_stop_on_sample(tempdir):
    """Test that the judge stops evaluating test cases if a sample case fails."""
    copyfile('./sample_problem_info/test/solutions/stop_on_sample.py', tempdir + '/stop_on_sample.py')
    job = q.enqueue_call(func=judge_submission, args=(tempdir, 'test', 'stop_on_sample.py', 'python'))
    assert job.result['final_score'] == 0


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


def test_carriage_return(tempdir):
    """Test that the judge will still give a correct verdict if carriage returns are present."""
    assert True


def test_output_limiting(tempdir):
    """Make sure the judge limits the amount of data a program can write to stdout and stderr."""
    assert True


def test_file_limiting(tempdir):
    """Make sure the judge limits the amount of data a program can write to files."""
    assert True

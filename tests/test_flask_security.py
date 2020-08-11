"""
This test batch makes sure the API does not allow unauthorized users to access it.
"""

import sys
from time import sleep

sys.path.append('./')

import io
import pytest
import app
from misc.env_vars import *


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_queuing_system(client):
    """Test the submission queuing system to make sure it actually works."""
    # Submit 2 times
    job1 = eval(client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'while True: x = 3'), 'code.py'),
        username='user_queue1',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data').data)['job_id']
    job2 = eval(client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='user_queue2',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data').data)['job_id']

    # Wait a bit for jobs to start getting judged
    sleep(1.5)

    # Immediately check status of job1 (should be judging)
    rv = client.get('/api/get_status/{}'.format(job1))
    assert b'judging' in rv.data
    # Immediately check status of job2 (should be in queue)
    rv = client.get('/api/get_status/{}'.format(job2))
    assert b'queued' in rv.data

    # Wait for jobs to complete
    sleep(5.5)

    # Make sure both jobs are done
    rv = client.get('/api/get_status/{}'.format(job1))
    assert b'done' in rv.data
    rv = client.get('/api/get_status/{}'.format(job2))
    assert b'done' in rv.data and b'101' in rv.data


def test_get_submissions_no_key(client):
    """Make sure users cannot get submissions without the secret key."""
    rv = client.get('/api/get_submissions/1')
    assert b'Missing secret key' in rv.data


def test_get_submissions_wrong_key(client):
    """Make sure users cannot get submissions with an invalid secret key."""
    rv = client.get('/api/get_submissions/1', query_string=dict(secret_key='hi'))
    assert b'Invalid secret key' in rv.data


def test_submit_no_key(client):
    """Make sure the right error is returned for a POST request with no secret key."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='test_user'
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Missing secret key' in rv.data


def test_submit_wrong_key(client):
    """Make sure users cannot submit code with an invalid secret key."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='test_user',
        secret_key='hi'
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid secret key' in rv.data

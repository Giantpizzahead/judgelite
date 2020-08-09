"""
This test batch makes sure the frontend Flask application's interface works as expected.
"""

import sys

sys.path.append('./')

from time import sleep
import io
import pytest
import app
from env_vars import *

valid_job_id: str


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_landing_page(client):
    """Make sure the landing page loads without throwing an error."""
    rv = client.get('/')
    assert b'Welcome to JudgeLite' in rv.data


def test_problem_list(client):
    """Make sure the problem list loads correctly."""
    rv = client.get('/problem_list')
    assert b'Problem List' in rv.data and b'test4' in rv.data


def test_submit_form(client):
    """Make sure sending a GET request to /api/submit results in a test submission form."""
    rv = client.get('/api/submit')
    assert b'Test Submission Form' in rv.data


def test_get_login_form(client):
    """Make sure the login page works."""
    rv = client.get('/login')
    assert b'Login Form' in rv.data


def test_login_as_admin(client):
    """Test the process of logging in / out as the admin."""
    client.post('/login', data=dict(
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    rv = client.get('/submission_list')
    assert b'Submission List' in rv.data
    client.get('/logout')
    rv = client.get('/submission_list')
    assert b'Submission List' not in rv.data


def test_failed_admin_login(client):
    """Test the process of logging in as the admin with a wrong password."""
    rv = client.post('/login', data=dict(
        secret_key='OPEN SESAME'
    ), follow_redirects=True, content_type='multipart/form-data')
    client.get('/logout')
    assert b'Incorrect secret key' in rv.data


def test_submission_list_blocked(client):
    """Make sure the submission list is blocked for non-admins."""
    rv = client.get('/submission_list')
    assert b'Submission List' not in rv.data


def test_submission_list(client):
    """Make sure the submission list works for admins."""
    # Make a submission
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='VERY_UNIQUE_USERNAME_HERE',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    global valid_job_id
    valid_job_id = eval(rv.data)['job_id']
    # Make sure submission finishes to avoid issues
    sleep(2)

    client.post('/login', data=dict(
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    rv = client.get('/submission_list')
    assert b'VERY_UNIQUE_USERNAME_HERE' in rv.data


def test_submission_details(client):
    """Make sure the submission details display as expected."""
    rv = client.get('/submission_details?job_id={}'.format(valid_job_id))
    assert b'Submission Details' in rv.data and b'print' in rv.data and b'VERY_UNIQUE_USERNAME_HERE' in rv.data

"""
This test batch makes sure the Flask API works as expected.
"""

import sys
sys.path.append('./')

from time import sleep
import io
import pytest
import app
from misc.env_vars import *

valid_job_id: str


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_get_problem_list(client):
    """Test the process of getting the list of problems."""
    rv = client.get('/api/get_problem_list')
    assert b'sample2' in rv.data and b'test4' in rv.data


def test_get_problem_info(client):
    """Test the process of getting problem info."""
    rv = client.get('/api/get_problem_info/test')
    assert b'This problem serves as a way for you to test the submission system.' in rv.data


def test_submit(client):
    """Test the process of submitting code."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    # Make sure submission finishes to avoid issues
    sleep(2)
    assert b'success' in rv.data
    # Save job_id to be used later in the tests
    rv = eval(rv.data)
    global valid_job_id
    valid_job_id = rv['job_id']


def test_submit_no_form(client):
    """Make sure the right error is returned for an empty POST request."""
    rv = client.post('/api/submit', data=None, follow_redirects=True, content_type='multipart/form-data')
    assert b'Empty request form' in rv.data


def test_submit_no_id(client):
    """Make sure the right error is returned for a POST request with no id."""
    rv = client.post('/api/submit', data=dict(
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid problem ID' in rv.data


def test_submit_invalid_id(client):
    """Make sure the right error is returned for a POST request with an invalid id."""
    rv = client.post('/api/submit', data=dict(
        problem_id='lol_no_this_is_very_invalid_id',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid problem ID' in rv.data


def test_submit_no_type(client):
    """Make sure the right error is returned for a POST request with no language type."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'No submission language' in rv.data


def test_submit_invalid_type(client):
    """Make sure the right error is returned for a POST request with an invalid language type."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='brainf*ck',
        code=(io.BytesIO(b'+[-->-[>>+>-----<<]<--<---]>-.>>>+.>>..+++[.>]<<<<.+++.------.<<-.>>>>+.'), 'code.bf'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid submission language' in rv.data


def test_submit_no_code(client):
    """Make sure the right error is returned for a POST request with no code."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'No code file submitted' in rv.data


def test_submit_invalid_filename(client):
    """Make sure the right error is returned for a POST request with an invalid code filename."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'input.in.txt'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid code filename' in rv.data


def test_submit_invalid_extensions(client):
    """Make sure the right error is returned for POST requests with invalid extensions."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='java',
        code=(io.BytesIO(b'public class java {}\n'), 'java.cpp'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Missing .java file extension' in rv.data

    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='cpp',
        code=(io.BytesIO(b'#include <iostream>\n'), 'cpp.py'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Missing .cpp file extension' in rv.data

    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'if __name__ == "__main__": main()\n'), 'py.java'),
        username='test_user',
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Missing .py file extension' in rv.data


def test_submit_no_username(client):
    """Make sure the right error is returned for a POST request with no username."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py'),
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    # Make sure submission finishes to avoid issues
    assert b'No username' in rv.data


def test_get_status_invalid_job(client):
    """Make sure invalid job ids sent to /api/get_status return the right JSON error."""
    rv = client.get('/api/get_status/abacadabra')
    assert b'NO_SUCH_JOB' in rv.data


def test_get_status(client):
    """Make sure /api/get_status returns the expected result."""
    rv = client.get('/api/get_status/{}'.format(valid_job_id))
    assert b'"status":"done"' in rv.data and b'101' in rv.data


def test_get_submissions(client):
    """Make sure the get submissions API call works correctly."""
    rv = client.get('/api/get_submissions/1', query_string=dict(secret_key=SECRET_KEY))
    assert valid_job_id.encode('utf-8') in rv.data and b'101' in rv.data


def test_get_source(client):
    """Make sure the get submission source API call works correctly."""
    rv = client.get('/api/get_submission_source/{}'.format(valid_job_id))
    assert b'N=int(input())' in rv.data

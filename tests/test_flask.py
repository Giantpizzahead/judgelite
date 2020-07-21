"""
This test batch makes sure the frontend Flask application works as expected.
"""

import sys
sys.path.append('./')

from time import sleep
from flask import *
import io
import pytest
import app


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_submit(client):
    """Test the process of submitting code."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py')
    ), follow_redirects=True, content_type='multipart/form-data')
    # Make sure submission finishes to avoid issues
    sleep(2)
    assert b'submission-result-box' in rv.data


def test_submit_no_form(client):
    """Make sure the right error is returned for an empty POST request."""
    rv = client.post('/api/submit', data=None, follow_redirects=True, content_type='multipart/form-data')
    assert b'Empty request form' in rv.data


def test_submit_no_id(client):
    """Make sure the right error is returned for a POST request with no id."""
    rv = client.post('/api/submit', data=dict(
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py')
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid problem ID' in rv.data


def test_submit_invalid_id(client):
    """Make sure the right error is returned for a POST request with an invalid id."""
    rv = client.post('/api/submit', data=dict(
        problem_id='lol_no_this_is_very_invalid_id',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py')
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid problem ID' in rv.data


def test_submit_no_type(client):
    """Make sure the right error is returned for a POST request with no language type."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'code.py')
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'No submission language' in rv.data


def test_submit_invalid_type(client):
    """Make sure the right error is returned for a POST request with an invalid language type."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='brainf*ck',
        code=(io.BytesIO(b'+[-->-[>>+>-----<<]<--<---]>-.>>>+.>>..+++[.>]<<<<.+++.------.<<-.>>>>+.'), 'code.bf')
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid submission language' in rv.data


def test_submit_no_code(client):
    """Make sure the right error is returned for a POST request with no code."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python'
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'No code file submitted' in rv.data


def test_submit_invalid_filename(client):
    """Make sure the right error is returned for a POST request with an invalid code filename."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='python',
        code=(io.BytesIO(b'N=int(input())\nprint(N)\n'), 'input.in.txt')
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Invalid code filename' in rv.data


def test_submit_invalid_java_extension(client):
    """Make sure the right error is returned for a POST request with an invalid java extension."""
    rv = client.post('/api/submit', data=dict(
        problem_id='test',
        type='java',
        code=(io.BytesIO(b'public class java {}\n'), 'java.cpp')
    ), follow_redirects=True, content_type='multipart/form-data')
    assert b'Missing .java file extension' in rv.data


def test_invalid_job_errors(client):
    """Make sure invalid job ids sent to /status return the right user-friendly error."""
    rv = client.get('/status?job_id=abacadabra')
    assert b'Job not found' in rv.data


def test_invalid_job_redirect(client):
    """Make sure invalid job ids sent to /api/results return the right JSON error."""
    rv = client.get('/api/results/abacadabra')
    assert b'NO_SUCH_JOB' in rv.data

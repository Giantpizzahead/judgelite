"""
This test batch makes sure the frontend Flask application works as expected.

There isn't much here right now, but more tests will be added once a problem editing interface is made.
"""

import sys
sys.path.append('./')

import pytest
import app


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_invalid_job_errors(client):
    """Make sure invalid job ids sent to /status return the right user-friendly error."""
    rv = client.get('/status?job_id=abacadabra')
    assert b'Job not found' in rv.data


def test_invalid_job_redirect(client):
    """Make sure invalid job ids sent to /result return the right JSON error."""
    rv = client.get('/results/abacadabra')
    assert b'NO_SUCH_JOB' in rv.data

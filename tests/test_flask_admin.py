"""
This test batch makes sure the frontend Flask application's admin interface works as expected.
"""

import sys
sys.path.append('./')

from time import sleep
import io
import pytest
import app
from env_vars import *


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_get_login_form(client):
    """Make sure the login page works."""
    rv = client.get('/login')
    assert b'Login Form' in rv.data


def test_login_as_admin(client):
    """Test the process of logging in as the admin."""
    rv = client.post('/login', data=dict(
        secret_key=SECRET_KEY
    ), follow_redirects=True, content_type='multipart/form-data')
    client.get('/logout')
    assert not b'Incorrect secret key' in rv.data


def test_failed_admin_login(client):
    """Test the process of logging in as the admin with a wrong password."""
    rv = client.post('/login', data=dict(
        secret_key='OPEN SESAME'
    ), follow_redirects=True, content_type='multipart/form-data')
    client.get('/logout')
    assert b'Incorrect secret key' in rv.data

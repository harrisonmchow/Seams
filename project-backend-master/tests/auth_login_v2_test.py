'''
This test fle aims to validate the functionality of the auth_login_v2 function.
Using pytest, this file verifies whether a user is correctly being logged into the system.

Functions:
    test_login_incorrect_email()
    test_incorrect_password()
    test_correct_token()
'''
import pytest
import jwt
from src.error import InputError
import requests
import json
from src.config import url
BASE_URL = url


@pytest.fixture
def clear_reg():
    print(f"{BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")

    assert response.status_code == 200


@pytest.fixture
def register_user():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email1@gmail.com", "password": "password1", "name_first": "first", "name_last": "last"})
    return response.json()


def test_login_incorrect_email(clear_reg, register_user):
    '''
    Tests that auth_login_v1 correctly denies an incorrect email address
    '''
    response = requests.post(f"{BASE_URL}/auth/login/v2", json={'email': 'Homer.Simpson@unsw.edu.au',
                             'password': 'password'})

    assert response.status_code == InputError.code


def test_incorrect_password(clear_reg, register_user):
    '''
    Verifies that auth_login_v1 declines an incorrect password
    '''
    response = requests.post(f"{BASE_URL}/auth/login/v2", json={
                             'email': 'gerard.mathews@unsw.edu.au', 'password': 'wrongpassword'})
    assert response.status_code == InputError.code


def test_login_wrong_password(clear_reg):
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "harry@gmail.com", "password": "password12345",
                                              "name_first": "harry", "name_last": "chow"})
    response = requests.post(f"{BASE_URL}/auth/login/v2", json={
                             'email': 'harry@gmail.com', 'password': 'wrongpassword'})
    assert response.status_code == InputError.code


def test_correct_token(clear_reg):
    '''
    Verifies that auth_login_v2 correctly generates a new JWT
    '''
    requests.post(
        f"{BASE_URL}/auth/register/v2", json={'email': 'gerard.mathews@unsw.edu.au', 'password': 'password1', 'name_first': 'first', 'name_last': 'last'})
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={'email': 'gerard.mathews@unsw.edu.au', 'password': 'password1'})
    response = json.loads(response.text)
    token = jwt.decode(response['token'],
                       key="BADGER", algorithms=['HS256'])
    assert token['auth_user_id'] == 1

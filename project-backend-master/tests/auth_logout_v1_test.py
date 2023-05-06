'''
This test fle aims to validate the functionality of the auth_logout_v1 function.
Using pytest, this file verifies whether auth_logout correctly removes a token from the session 
list.

Functions:
    test_valid_input()
    test_invalid_token()
    test_two_simultaneous_logins()
    test_login_two_tabs_logout_one()
    test_two_consecutive_logouts()
'''
import pytest
from src.error import AccessError
import requests
from src.config import url
BASE_URL = url


@pytest.fixture
def clear_register():
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password",
                                   "name_first": "John", "name_last": "Smith"})
    user = response.json()
    return user


def test_valid_input(clear_register):
    '''
    Verify that running auth/logout/v1 following by auth/login/v1 causes an AccessError
    '''
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_response = response.json()
    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": login_response["token"]})

    assert response.status_code == 200


def test_invalid_token(clear_register):
    '''
    Verify that a user that is not logged in, cannot log out
    '''
    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": "invalid"})

    assert response.status_code == AccessError.code


def test_two_simultaneous_logins(clear_register):
    '''
    Verify that a user can login on two tabs, then logout on one and continue using the other.
    '''
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_1 = response.json()

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_2 = response.json()

    assert login_1["token"] != login_2["token"]


def test_login_two_tabs_logout_one():
    '''
    Verify that a user can login on two tabs, then logout on one and continue using the other.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    requests.post(f"{BASE_URL}/auth/register/v2",
                  json={"email": "john.smith@unsw.edu.au", "password": "password",
                        "name_first": "John", "name_last": "Smith"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_1 = response.json()

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_2 = response.json()

    requests.post(f"{BASE_URL}/auth/logout/v1",
                  json={"token": login_1["token"]})
    assert response.status_code == 200
    response = requests.get(
        f"{BASE_URL}/users/all/v1", params={"token": login_2["token"]})
    assert response.status_code == 200


def test_two_consecutive_logouts(clear_register):
    '''
    Verify that a user can login on two tabs, then logout on each tab consecutively.
    '''

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_1 = response.json()

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_2 = response.json()

    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": login_1["token"]})

    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": login_2["token"]})
    assert response.status_code == 200


def users_multiple_sessions(clear_register):
    # two people with active sessions. Then log them both out
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    login_1 = response.json()

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "bob.smith@unsw.edu.au", "password": "password",
                                   "name_first": "Bob", "name_last": "Smith"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "bob.smith@unsw.edu.au", "password": "password"})
    login_2 = response.json()

    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": login_1["token"]})

    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": login_2["token"]})
    assert response.status_code == 200

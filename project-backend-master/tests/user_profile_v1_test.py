'''
This script verifies the functionality of user_profile. It assesses whether user_profile picks up
error an invalid token and returns the correct dictionary. 

Functions: 
    test_invalid_token()
    test_profile_success()

'''


import pytest
import json
from src.auth import auth_register_v2
from src.other import clear_v1
from src.error import AccessError, InputError
import requests
from src.config import url
BASE_URL = url


@pytest.fixture
def setup():
    clear_v1()
    user_id1 = auth_register_v2(
        "harry@unsw.edu.au", "Password123", "harry", "chow")
    user_id2 = auth_register_v2(
        "jack@unsw.edu.au", "Comp1531iseasy", "jack", "adams")
    user_id3 = auth_register_v2(
        'email1@gmail.com', 'password1', 'first', 'last')
    user_id4 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')

    return [user_id1['auth_user_id'], user_id2['auth_user_id'], user_id3['auth_user_id'], user_id4['auth_user_id']]


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


@pytest.fixture
def login_user():
    response = requests.post(
        f"{BASE_URL}/auth/login/v2", json={"email": "email1@gmail.com", "password": "password1"})
    return response.json()


def test_invalid_token(clear_reg, register_user):
    '''
    This test verifies that it correctly indentifies an invalid token
    '''
    response = requests.get(
        f"{BASE_URL}/user/profile/v1", params={"token": "wefwrg", "u_id": 1})
    assert response.status_code == AccessError.code


def test_profile_success(clear_reg, register_user, login_user):
    '''
    This test verifies the correct funtion of user_profile_v1
    '''
    response = login_user

    response = requests.get(
        f"{BASE_URL}/user/profile/v1", params={"token": response['token'], "u_id": 1})

    response = json.loads(response.text)
    assert response['user']['u_id'] == 1
    assert response['user']['email'] == 'email1@gmail.com'
    assert response['user']['name_first'] == 'first'
    assert response['user']['name_last'] == 'last'
    assert response['user']['handle_str'] == 'firstlast'


def test_invalid_u_id(clear_reg, register_user, login_user):
    response = login_user
    response2 = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email2@gmail.com", "password": "password1", "name_first": "first", "name_last": "last"})
    assert response2.status_code == 200
    response3 = requests.get(
        f"{BASE_URL}/user/profile/v1", params={"token": response['token'], "u_id": 5})
    assert response3.status_code == InputError.code

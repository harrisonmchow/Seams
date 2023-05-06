'''
This test file aims to assess the functionaility of the auth_password_reset_reset function.

Functions:
    test_invalid_password()
    test_incorrect_code()
    tset_function_success()
'''
import pytest
from src.data_store import U_PASSWORD_IDX, U_PW_RESET_CODE_IDX, data_store
import requests
from src.config import url
import json

BASE_URL = url

# verify data_store (whitebox)
# invalidate code
# incorrect code
# invalid password

# potential assumption for logging in user before reset


@pytest.fixture
def clear_reg():
    print(f"{BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")

    assert response.status_code == 200


@pytest.fixture
def register_user():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "harry@gmail.com", "password": "password0",
                                              "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "gerardmathews02@gmail.com", "password": "password1",
                                              "name_first": "first", "name_last": "last"})
    assert response.status_code == 200
    return response.json()  # returns token and auth user id


def test_invalid_password(clear_reg, register_user):
    '''
    tests an invalid new password
    '''
    # requests.post(f"{BASE_URL}/auth/password/reset/request/v1",
    #   json={"email": "email1@gmail.com"})
    # store = data_store.get()
    reset_code = 643325
    response = requests.post(
        f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": reset_code,
                                                         "new_password": "pw"})
    assert response.status_code == 400


def test_incorrect_code(clear_reg, register_user):
    '''
    tests an incorrect security code
    '''
    # requests.post(f"{BASE_URL}/auth/password/reset/request/v1",
    #               json={"email": "gerardmathews02@gmail.com"})
    response = requests.post(
        f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": 9999,
                                                         "new_password": "ps"})
    assert response.status_code == 400


def test_function_success(clear_reg, register_user):
    '''
    test the correct functionality of password reset. Attempts to re-login the user with the new password
    '''

    response = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1",
                             json={"email": "gerardmathews02@gmail.com"})
    assert response.status_code == 200

    with open('src/data_store.json', 'r', encoding="utf8") as file:
        file_contents = json.load(file)

    reset_code = file_contents['users'][1][U_PW_RESET_CODE_IDX]['reset_code']
    password = file_contents['users'][1][U_PASSWORD_IDX]
    print(password)

    response = requests.post(
        f"{BASE_URL}/auth/passwordreset/reset/v1", json={"reset_code": reset_code,
                                                         "new_password": "password"})
    assert response.status_code == 200

    with open('src/data_store.json', 'r', encoding="utf8") as file:
        file_contents = json.load(file)

    reset_code = file_contents['users'][1][U_PW_RESET_CODE_IDX]['reset_code']
    password = file_contents['users'][1][U_PASSWORD_IDX]
    print(password)

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "gerardmathews02@gmail.com", "password": "password"})

    assert response.status_code == 200

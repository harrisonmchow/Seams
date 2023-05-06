'''
This test fle aims to validate the functionality of the auth_register_v2 function.
Using pytest, this file verifies whether auth_register_v2 is correctly identifying errors,
(such as invalid email format or password) and whether the creation of user_id and token is
correctly occurring.

Functions:
    test_register_invalid_email()
    test_register_duplicated_email()
    test_invalid_password()
    test_invalid_first_name()
    test_invalid_last_name()
    test_successive_registers()
    test_string_handle_duplicates()
    test_short_password()
    test_long_and_short_names()
'''
import jwt
import pytest
import requests
from src.auth import auth_register_v2
from src.error import InputError
from src.other import clear_v1
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


def test_register_invalid_email(clear_reg):
    '''
    Tests whether auth_register_v1 can accurately validate email formatting
    '''
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "gerard.mathews.unsw.edu.au", "password": "password1", "name_first": "first", "name_last": "last"})

    assert response.status_code == InputError.code

    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "gerard.mathews@@unsw.edu.au", "password": "password1", "name_first": "first", "name_last": "last"})

    assert response.status_code == InputError.code

    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "gerard.%^(@unsw.edu.au", "password": "password1", "name_first": "first", "name_last": "last"})

    assert response.status_code == InputError.code

    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "gerard.mathews@", "password": "password1", "name_first": "first", "name_last": "last"})

    assert response.status_code == InputError.code

    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "@gerard.mathews.unsw.edu.au", "password": "password1", "name_first": "first", "name_last": "last"})

    assert response.status_code == InputError.code


def test_register_duplicated_email(clear_reg, register_user):
    '''
    Verifies whether auth_register_v1 declines a user registering the same email twice
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "email1@gmail.com",
                             "password": "password1", "name_first": "first", "name_last": "last"})

    assert response.status_code == InputError.code


def test_invalid_password():
    '''
    Tests whether password formatting is being properly enforced
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2('gerard.mathews@unsw.edu.au', '',
                         'gerard', 'mathews')  # Password 0 characters long
    with pytest.raises(InputError):
        auth_register_v2('gerard.mathews@unsw.edu.au', '12345',
                         'gerard', 'mathews')  # Password 5 characters long


def test_invalid_first_name():
    '''
    Verifies if a user's first name is between 1-50 characters
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2('gerard.mathews@unsw.edu.au',
                         'password', '', 'mathews')  # No name entry

    with pytest.raises(InputError):
        # First name 51 characters long
        auth_register_v2('gerard.mathews@unsw.edu.au', 'password',
                         'LoUwfNkfzB0RpQslXkJWc3VeeVRizUyvFBw4zczw3aBoxlzAF4l', 'mathews')


def test_invalid_last_name():
    '''
    Verifies if a user's last name is between 1-50 characters
    '''
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v2('gerard.mathews@unsw.edu.au',
                         'password', 'gerard', '')  # No name entry

    with pytest.raises(InputError):
        # Last name 51 characters long
        auth_register_v2('gerard.mathews@unsw.edu.au', 'password', 'gerard',
                         'LoUwfNkfzB0RpQslXkJWc3VeeVRizUyvFBw4zczw3aBoxlzAF4l')


def test_successive_registers():
    '''
    Tests whether auth_register_v1 creates the correct user_id
    '''
    clear_v1()
    return_register_1 = auth_register_v2(
        'gerard.mathews@unsw.edu.au', 'password', 'gerard', 'mathews')
    token_register_1 = jwt.decode(
        return_register_1['token'], key="BADGER", algorithms=['HS256'])

    return_register_2 = auth_register_v2(
        'gerard.mathews1@unsw.edu.au', 'password', 'gerard', 'mathews')
    token_register_2 = jwt.decode(
        return_register_2['token'], key="BADGER", algorithms=['HS256'])

    assert token_register_2['auth_user_id'] == token_register_1['auth_user_id'] + \
        1, "Unexpected user_ID"


def test_string_handle_duplicates(clear_reg):
    '''
    This function tests the case of duplicated handles
    '''
    for i in range(5):
        response = requests.post(f"{BASE_URL}/auth/register/v2",
                                 json={"email": f"user{i}@unsw.edu.au", "password": "password1", "name_first": "firstname", "name_last": "lastname"})
        assert response.status_code == 200


def test_short_password(clear_reg):
    '''
    This test verifies auth_register's ability to detect password input errors
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "user1@unsw.edu.au", "password": "short", "name_first": "first", "name_last": "last"})
    assert response.status_code == InputError.code


def test_long_and_short_names(clear_reg):
    '''
    This test verifies auth_register's ability to detect name input errors
    '''
    # no first name
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "user1@unsw.edu.au", "password": "short_changed", "name_first": "", "name_last": "last"})
    assert response.status_code == InputError.code
    # long first name
    first_name = "LnUnrdGpByjZZKMBIauGtPjHkGsyEgfCINxHJASEdcStXVVIAQfClvbsBvDV"
    assert len(first_name) > 50
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "user1@unsw.edu.au", "password": "short_changed", "name_first": first_name, "name_last": "last"})
    assert response.status_code == InputError.code

    # no last name
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "user1@unsw.edu.au", "password": "short_changed", "name_first": "Tim", "name_last": ""})
    assert response.status_code == InputError.code
    # long last name
    last_name = "LnUnrdGpByjZZKMBIauGtPjHkGsyEgfCINxHJASEdcStXVVIAQfClvbsBvDV"
    assert len(last_name) > 50
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "user1@unsw.edu.au", "password": "short_changed", "name_first": "tim", "name_last": last_name})
    assert response.status_code == InputError.code


def test_register_remove_then_register(clear_reg):
    response1 = requests.post(f"{BASE_URL}/auth/register/v2",
                              json={"email": "user1@unsw.edu.au", "password": "Password12345", "name_first": "first", "name_last": "last"})
    assert response1.status_code == 200
    login = requests.post(f"{BASE_URL}/auth/login/v2",
                          json={"email": "user1@unsw.edu.au", "password": "Password12345"})
    assert login.status_code == 200
    token = login.json()['token']

    response2 = requests.post(f"{BASE_URL}/auth/register/v2",
                              json={"email": "user2@unsw.edu.au", "password": "Password12345", "name_first": "bob", "name_last": "dylan"})
    assert response2.status_code == 200
    u_id = response2.json()['auth_user_id']
    # remove the second user
    delete = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token, "u_id": u_id})
    assert delete.status_code == 200
    # re-register using the email
    response2 = requests.post(f"{BASE_URL}/auth/register/v2",
                              json={"email": "user2@unsw.edu.au", "password": "Password12345", "name_first": "bob", "name_last": "dylan"})
    assert response2.status_code == 200

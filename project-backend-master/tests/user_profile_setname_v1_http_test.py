'''
This test fle aims to validate the functionality of the user_profile_setname_v1
function using pytest.

Functions:
    clear_register_and_login_user()
    test_valid_first_name()
    test_valid_last_name()
    test_first_name_too_long()
    test_first_name_too_short()
    test_last_name_too_long()
    test_last_name_too_short()
'''
import pytest
import requests
from src.error import InputError
from src.config import url


BASE_URL = url


@pytest.fixture
def clear_register_and_login_user():
    '''
    This function is a fixture used to clear the system, register
    a new user and login this new user.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password",
                                   "name_first": "John", "name_last": "Smith"})

    user = response.json()

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "bob.smith@unsw.edu.au", "password": "password",
                                   "name_first": "bob", "name_last": "Smith"})
    user2 = response.json()
    return user, user2


def test_valid_first_name(clear_register_and_login_user):
    '''
    Test a valid change of first name.
    '''
    user = clear_register_and_login_user[0]

    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user['token'], "name_first": "Tom", "name_last": "Smith"})

    assert response.status_code == 200


def test_valid_last_name(clear_register_and_login_user):
    '''
    Test a valid change of last name.
    '''
    user, user2 = clear_register_and_login_user

    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user2['token'], "name_first": "Bob", "name_last": "Green"})

    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user['token'], "name_first": "John", "name_last": "Green"})

    assert response.status_code == 200


def test_first_name_too_long(clear_register_and_login_user):
    '''
    Test that a first name with 51 characters is invalid.
    '''
    user = clear_register_and_login_user[0]
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user['token'], "name_first":
                                  "AF1L6NqMIpEjiAvyUGxso4RkDcJOx5hVl6Jonl0zF453OaCGT9b", "name_last": "Smith"})

    assert response.status_code == InputError.code


def test_first_name_too_short(clear_register_and_login_user):
    '''
    Test that a first name with 0 characters is invalid.
    '''
    user = clear_register_and_login_user[0]
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user['token'], "name_first": "", "name_last": "Smith"})

    assert response.status_code == InputError.code


def test_last_name_too_long(clear_register_and_login_user):
    '''
    Test that a last name with 51 characters is invalid.
    '''
    user = clear_register_and_login_user[0]
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user['token'], "name_first":
                                  "John", "name_last": "AF1L6NqMIpEjiAvyUGxso4RkDcJOx5hVl6Jonl0zF453OaCGT9b"})

    assert response.status_code == InputError.code


def test_last_name_too_short(clear_register_and_login_user):
    '''
    Test that a last name with 0 characters is invalid.
    '''
    user = clear_register_and_login_user[0]
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1",
                            json={"token": user['token'], "name_first": "John", "name_last": ""})

    assert response.status_code == InputError.code


def test_dm_name_change(clear_register_and_login_user):
    '''
    Runs the reset name method, ensures that the name of user
    in DM has been updated.
    This test is necessary due to how DM stores its members
    HTTP test
    '''
    user = clear_register_and_login_user[0]

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "kson@vtub.er", "password": "password",
                                   "name_first": "Kson", "name_last": "Onair"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "kson@vtub.er", "password": "password"})
    assert response.status_code == 200
    user_2 = response.json()

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "aloe.x@holo.grad", "password": "password",
                                   "name_first": "aloe", "name_last": "x"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "aloe.x@holo.grad", "password": "password"})
    assert response.status_code == 200
    user_3 = response.json()

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user['token'],
                                   'u_ids': []})
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user['token'],
                                   'u_ids': [user_3['auth_user_id'], user_2['auth_user_id']]})
    assert response.status_code == 200
    dm_info = response.json()

    response = requests.put(
        f'{BASE_URL}/user/profile/setname/v1',
        json={'token': user['token'],
              'name_first': 'felix',
              'name_last': 'li'})

    response = requests.put(
        f'{BASE_URL}/user/profile/setname/v1',
        json={'token': user_2['token'],
              'name_first': 'kiryu',
              'name_last': 'coco'})

    response = requests.put(
        f'{BASE_URL}/user/profile/setname/v1',
        json={'token': user_3['token'],
              'name_first': 'mano',
              'name_last': 'aloe'})

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            {'token': user['token'],
                             'dm_id': dm_info['dm_id']})
    assert response.status_code == 200
    output = response.json()
    assert output['members'][-1]['name_first'] == 'felix'
    assert output['members'][-1]['name_last'] == 'li'
    assert output['members'][0]['name_first'] == 'mano'
    assert output['members'][0]['name_last'] == 'aloe'
    assert output['members'][1]['name_first'] == 'kiryu'
    assert output['members'][1]['name_last'] == 'coco'

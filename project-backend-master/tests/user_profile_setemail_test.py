'''
This test fle aims to validate the functionality of the user_profile_setemail_v1
function using pytest.

Functions:
    clear_register_and_login_user()
    test_invalid_email()
    test_valid_email()
    test_email_already_used()
    
'''
import pytest
import requests
from src.error import InputError
from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_and_login_user():
    '''
    A fixture which registers and logs in a user.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password",
                                   "name_first": "John", "name_last": "Smith"})

    user = response.json()
    return user


@pytest.fixture
def register_another_user():
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "bob.smith@unsw.edu.au", "password": "password",
                                   "name_first": "Bob", "name_last": "Smith"})
    assert response.status_code == 200


def test_invalid_email(clear_register_and_login_user):
    '''
    Tests invlaid email formats
    '''
    user = clear_register_and_login_user

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "plaintext"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "#@%^%#$@#$@#.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "@fail.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "John Smith <email@example.com>"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email.fail.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@fail@example.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "あいうえお@fail.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@fail.com (John Smith)"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@fail"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@111.666.777.44444"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": r"”(),:;<>[\]@fail.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "just”not”right@fail.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": r"this\ is'really'not/allowed@fail.com"})
    assert response.status_code == InputError.code

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": ""})
    assert response.status_code == InputError.code


def test_valid_email(clear_register_and_login_user, register_another_user):
    '''
    Tests valid email formats
    '''
    register_another_user
    user = clear_register_and_login_user

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@valid.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "firstname.lastname@valid.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@subdomain.valid.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "firstname+lastname@valid.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "1234567890@valid.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@valid-one.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "_______@valid.com"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@valid.name"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@valid.museum"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "email@valid.co.jp"})
    assert response.status_code == 200

    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "firstname-lastname@valid.com"})
    assert response.status_code == 200


def test_email_already_used(clear_register_and_login_user):
    '''
    Tests an email address already used by another user
    '''
    user = clear_register_and_login_user
    response = requests.put(
        f"{BASE_URL}/user/profile/setemail/v1", json={"token": user['token'], "email": "john.smith@unsw.edu.au"})
    assert response.status_code == InputError.code


def test_dm_email_change(clear_register_and_login_user):
    '''
    Runs the reset email method, ensures that the email of user
    in DM has been updated.
    This test is necessary due to how DM stores its members
    HTTP test
    '''
    user = clear_register_and_login_user

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
        f'{BASE_URL}/user/profile/setemail/v1',
        json={'token': user['token'],
              'email': 'felix.li@unsw.edu.au'})

    response = requests.put(
        f'{BASE_URL}/user/profile/setemail/v1',
        json={'token': user_2['token'],
              'email': 'kson.onair@vtub.er'})

    response = requests.put(
        f'{BASE_URL}/user/profile/setemail/v1',
        json={'token': user_3['token'],
              'email': 'mano.aloe@holo.grad'})

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            {'token': user['token'],
                             'dm_id': dm_info['dm_id']})
    assert response.status_code == 200
    output = response.json()
    assert output['members'][-1]['u_id'] == user['auth_user_id']
    assert output['members'][-1]['email'] == 'felix.li@unsw.edu.au'
    assert output['members'][0]['email'] == 'mano.aloe@holo.grad'
    assert output['members'][1]['email'] == 'kson.onair@vtub.er'

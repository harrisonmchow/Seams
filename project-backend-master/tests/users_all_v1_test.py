'''
This test fle aims to validate the functionality of the users_all_v1
function using pytest.

Functions:
    clear_register_and_login_user()
    test_valid_input()
    test_correct_return_type()
   
'''
import pytest
import requests
from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_and_login_user():
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password",
                                   "name_first": "John", "name_last": "Smith"})
    user = response.json()

    return user


def test_valid_input_users_all(clear_register_and_login_user):
    user = clear_register_and_login_user
    response = requests.get(f"{BASE_URL}/users/all/v1",
                            params={"token": user["token"]})
    assert response.status_code == 200


def test_correct_return_type_users_all(clear_register_and_login_user):
    user = clear_register_and_login_user
    response = requests.get(f"{BASE_URL}/users/all/v1",
                            params={"token": user["token"]})

    users_list = response.json()
    user_0 = 0

    assert isinstance(users_list, dict) is True
    assert isinstance(users_list['users'], list) is True
    assert isinstance(users_list['users'][user_0]['email'], str) is True
    assert isinstance(users_list['users'][user_0]['name_first'], str) is True
    assert isinstance(users_list['users'][user_0]['name_last'], str) is True
    assert isinstance(users_list['users'][user_0]['handle_str'], str) is True


def test_join_users_then_remove(clear_register_and_login_user):
    user = clear_register_and_login_user
    token = user['token']

    # register and log in another user
    requests.post(f"{BASE_URL}/auth/register/v2",
                  json={"email": "ben.smith@unsw.edu.au", "password": "password",
                        "name_first": "Ben", "name_last": "Smith"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "ben.smith@unsw.edu.au", "password": "password"})
    user = response.json()
    u_id = user['auth_user_id']
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={'token': token,
                                                                         'u_id': u_id})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/users/all/v1",
                            params={"token": token})

    users_list = response.json()
    assert response.status_code == 200
    user_0 = 0
    assert users_list['users'][user_0]['email'] == "john.smith@unsw.edu.au"
    assert users_list['users'][user_0]['name_first'] == "John"
    assert users_list['users'][user_0]['name_last'] == "Smith"
    assert users_list['users'][user_0]['handle_str'] == "johnsmith"

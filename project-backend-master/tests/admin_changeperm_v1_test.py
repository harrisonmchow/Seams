import pytest
from src.auth import auth_register_v2
from src.other import clear_v1, encode_token
from src.error import InputError, AccessError
from src.user import change_userpermission

import requests
from src.config import url
BASE_URL = url

# Whitebox steup_____________________


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

# Blackbox setup__________________________________


@pytest.fixture
def clear_reg():
    print(f"{BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")

    assert response.status_code == 200


@pytest.fixture
def add_u1():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email1@gmail.com", "password": "password1", "name_first": "first", "name_last": "last"})
    assert response.status_code == 200

    return response.json()  # returns token and auth user id


@pytest.fixture
def add_u2():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email2@gmail.com", "password": "password2", "name_first": "firsttwo", "name_last": "lasttwo"})
    assert response.status_code == 200

    return response.json()  # returns token and auth user id


# ____________________________________________________________________________________
# Whitebox tests


def test_invalid_uid(setup):
    u1 = setup[0]
    with pytest.raises(InputError):
        change_userpermission(u1, 10, 1)


def test_no_global(setup):
    u1 = setup[0]
    with pytest.raises(InputError):
        change_userpermission(u1, u1, 2)


def test_invalid_pid(setup):
    u1 = setup[0]
    u2 = setup[1]
    with pytest.raises(InputError):
        change_userpermission(u1, u2, 50)


def test_already_perm(setup):
    u1 = setup[0]
    u2 = setup[1]

    change_userpermission(u1, u2, 1)
    with pytest.raises(InputError):
        change_userpermission(u1, u2, 1)


def test_invalid_auth(setup):
    u1 = setup[0]
    u2 = setup[1]

    with pytest.raises(AccessError):
        change_userpermission(u2, u1, 2)

# ____________________________________________________________________________
# HTTP Blakcbox TESTS


def test_correct_output(clear_reg, add_u1, add_u2):
    # InputError
    u1_token = add_u1['token']
    u2_id = add_u2['auth_user_id']
    p_id = 1
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == 200
    assert response.json() == {}


def test_http_inv_uid(clear_reg, add_u1):
    # InputError
    u1_token = add_u1['token']
    u2_id = 50
    p_id = 1
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == InputError.code


def test_remove_only_global(clear_reg, add_u1):
    # InputError
    u1_token = add_u1['token']
    u1_id = add_u1['auth_user_id']
    p_id = 2
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u1_id, "permission_id": p_id})
    assert response.status_code == InputError.code


def test_http_inv_pid(clear_reg, add_u1, add_u2):
    # InputError
    u1_token = add_u1['token']
    u2_id = add_u2['auth_user_id']
    p_id = 50
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == InputError.code


def test_http_already_perm(clear_reg, add_u1, add_u2):
    # InputError
    u1_token = add_u1['token']
    u2_id = add_u2['auth_user_id']
    p_id = 2
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == InputError.code


def test_http_not_auth(clear_reg, add_u1, add_u2):
    # InputError
    u1_id = add_u1['auth_user_id']
    u2_token = add_u2['token']
    p_id = 2

    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u2_token, "u_id": u1_id, "permission_id": p_id})
    assert response.status_code == AccessError.code


def test_http_dbl_err(clear_reg, add_u1, add_u2):
    # InputError
    u2_id = add_u2['auth_user_id']
    u2_token = add_u2['token']
    p_id = 50
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u2_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == AccessError.code


def test_http_adding(clear_reg, add_u1, add_u2):
    u1_token = add_u1['token']
    u2_id = add_u2['auth_user_id']
    p_id = 1
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == 200
    assert response.json() == {}


def test_http_removing(clear_reg, add_u1, add_u2):
    u1_token = add_u1['token']
    u2_id = add_u2['auth_user_id']
    p_id = 1
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == 200
    assert response.json() == {}
    p_id = 2
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": u1_token, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == 200
    assert response.json() == {}


def test_http_inv_auth(clear_reg, add_u1, add_u2):

    token1 = encode_token(-1)
    u2_id = add_u2['auth_user_id']
    p_id = 1
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": token1, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == AccessError.code


def test_http_inv_tok(clear_reg, add_u1, add_u2):

    token1 = 10
    u2_id = add_u2['auth_user_id']
    p_id = 1
    response = requests.post(
        f"{BASE_URL}/admin/userpermission/change/v1", json={"token": token1, "u_id": u2_id, "permission_id": p_id})
    assert response.status_code == AccessError.code

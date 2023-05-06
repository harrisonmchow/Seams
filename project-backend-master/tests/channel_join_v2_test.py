import pytest
import requests
from src.error import InputError, AccessError
from src.config import url
from src.other import encode_token
BASE_URL = url


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


def add_ch_1(token, name, is_public):
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": token, "name": name, "is_public": is_public})
    assert response.status_code == 200
    return response.json()
# ____________________________________________________________________________________-


def test_invalid_ch_id(clear_reg, add_u1, add_u2):
    # InputError
    u1_token = add_u1['token']
    ch_id = 1

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": u1_token, "channel_id": ch_id})
    assert response.status_code == InputError.code


def test_already_member(clear_reg, add_u1, add_u2):
    # InputError
    u1_token = add_u1['token']

    ch_id = add_ch_1(u1_token, "channel1", True)['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": u1_token, "channel_id": ch_id})
    assert response.status_code == InputError.code


def test_not_authorised(clear_reg, add_u1, add_u2):
    # AccessError
    u1_token = add_u1['token']

    u2_token = add_u2['token']

    ch_id = add_ch_1(u1_token, "channel1", False)['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": u2_token, "channel_id": ch_id})
    assert response.status_code == AccessError.code


def test_global_authorised(clear_reg, add_u1, add_u2):
    # AccessError
    u1_token = add_u1['token']

    u2_token = add_u2['token']

    ch_id = add_ch_1(u2_token, "channel1", False)['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": u1_token, "channel_id": ch_id})
    assert response.status_code == 200


def test_invalid_tok_http(clear_reg, add_u1, add_u2):
    u1_token = add_u1['token']
    u2_token = encode_token(-1)

    ch_id = add_ch_1(u1_token, "channel1", True)['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": u2_token, "channel_id": ch_id})
    assert response.status_code == AccessError.code

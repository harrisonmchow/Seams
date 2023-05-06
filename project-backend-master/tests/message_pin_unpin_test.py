from re import L
from urllib import response
import pytest
import requests
from src.error import InputError, AccessError
from datetime import datetime
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


@pytest.fixture
def add_u3():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email3@gmail.com", "password": "password3", "name_first": "firstthree", "name_last": "lastthree"})
    assert response.status_code == 200

    return response.json()  # returns token and auth user id


def add_ch(token, name, is_public):
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": token, "name": name, "is_public": is_public})
    assert response.status_code == 200
    return response.json()


def add_dm(token, u_ids):
    response = requests.post(
        f"{BASE_URL}/dm/create/v1", json={"token": token, "u_ids": u_ids})
    assert response.status_code == 200
    return response.json()

# ________________________________________________________________________

# MESSAGES
# invalid message id-ierror


def test_invalid_message_id(clear_reg, add_u1):
    token1 = add_u1['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    requests.post(f"{BASE_URL}/message/send/v1",
                  json={"token": token1, "channel_id": ch_id, "message": "Hello"})
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token1, "message_id": 10})
    assert response.status_code == InputError.code

    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token1, "message_id": 10})
    assert response.status_code == InputError.code

# already pinned-ierror


def test_already_pinned_unpinned(clear_reg, add_u1):
    token1 = add_u1['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": token1, "channel_id": ch_id, "message": "Hello"}).json()
    mid = response['message_id']
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token1, "message_id": mid})
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token1, "message_id": mid})
    assert response.status_code == InputError.code

    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token1, "message_id": mid})
    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token1, "message_id": mid})
    assert response.status_code == InputError.code

# not auth -aerror


def test_not_auth(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    token2 = add_u2['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": token1, "channel_id": ch_id, "message": "Hello"}).json()
    mid = response['message_id']
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token2, "message_id": mid})

    assert response.status_code == AccessError.code

    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token2, "message_id": mid})

    assert response.status_code == AccessError.code


# DMS

# invalid message id-ierror
def test_invalid_message_id_dm(clear_reg, add_u1):
    token1 = add_u1['token']

    dm_id = add_dm(token1, [])['dm_id']

    requests.post(f"{BASE_URL}/message/senddm/v1",
                  json={"token": token1, "dm_id": dm_id, "message": "Hello"})

    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token1, "message_id": 10})

    assert response.status_code == InputError.code
    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token1, "message_id": 10})
    assert response.status_code == InputError.code

# already pinned-ierror


def test_already_pinned_unpinned_dm(clear_reg, add_u1):
    token1 = add_u1['token']

    dm_id = add_dm(token1, [])['dm_id']

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": token1, "dm_id": dm_id, "message": "Hello"}).json()
    mid = response['message_id']
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token1, "message_id": mid})
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token1, "message_id": mid})

    assert response.status_code == InputError.code
    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token1, "message_id": mid})
    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token1, "message_id": mid})
    assert response.status_code == InputError.code

# not auth -aerror


def test_not_auth_dm(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    token2 = add_u2['token']
    dm_id = add_dm(token1, [])['dm_id']

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": token1, "dm_id": dm_id, "message": "Hello"}).json()
    mid = response['message_id']
    response = requests.post(f"{BASE_URL}/message/pin/v1",
                             json={"token": token2, "message_id": mid})

    assert response.status_code == AccessError.code

    response = requests.post(f"{BASE_URL}/message/unpin/v1",
                             json={"token": token2, "message_id": mid})

    assert response.status_code == AccessError.code

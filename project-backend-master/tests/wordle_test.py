from this import d
import pytest
from src.other import encode_token
from src.error import InputError, AccessError
import requests
from src.config import url
import json

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


def create_dm(token, u_ids):
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token,
                                                               "u_ids": u_ids})
    assert response.status_code == 200
    dm_id = response.json()['dm_id']
    return dm_id
# ________________________________________________________________________________________


def test_answer_correct_whitebox_ch(clear_reg, add_u1, add_u2):

    token1 = add_u1['token']
    token2 = add_u2['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token2, "channel_id": ch_id})
    assert response.status_code == 200

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200
    # _____WHITEBOX________________
    with open('src/data_store.json', 'r', encoding="utf8") as file:
        file_contents = json.load(file)

    answer = file_contents['wordle_ch'][ch_id]['wordle_answer']
    answer_rev = answer[::-1]
    print(answer)
    print(answer_rev)

    # _______________________________

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = f"/wordle {answer_rev}"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200
    msg = f"/wordle {answer}"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200


def test_not_started_end_ch(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    token2 = add_u2['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token2, "channel_id": ch_id})
    assert response.status_code == 200

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200


def test_not_in_bank_ch(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    token2 = add_u2['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token2, "channel_id": ch_id})
    assert response.status_code == 200

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = "/wordle oogaa"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code


def test_not_guessed_ch(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    token2 = add_u2['token']
    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token2, "channel_id": ch_id})
    assert response.status_code == 200

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200
    msg = "/wordle OOGABOOGA"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token2, "channel_id": ch_id, "message": msg})
    assert ans.status_code == InputError.code

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/send/v1",
                        json={"token": token1, "channel_id": ch_id, "message": msg})
    assert ans.status_code == 200

# _____________________________________________________________________________________________________


# _________________________________________________________------_________________________________________
def test_answer_correct_whitebox_dm(clear_reg, add_u1, add_u2):

    u2 = add_u2['auth_user_id']

    token1 = add_u1['token']
    token2 = add_u2['token']

    dm_id = create_dm(token1, [u2])

    msg = "/wordle start"

    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200
    # _____WHITEBOX________________
    with open('src/data_store.json', 'r', encoding="utf8") as file:
        file_contents = json.load(file)

    answer = file_contents['wordle_dm'][dm_id]['wordle_answer']
    answer_rev = answer[::-1]

    # _______________________________

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = f"/wordle {answer_rev}"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200
    msg = f"/wordle {answer}"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200


def test_not_started_end_dm(clear_reg, add_u1, add_u2):
    u2 = add_u2['auth_user_id']

    token1 = add_u1['token']
    token2 = add_u2['token']

    dm_id = create_dm(token1, [u2])

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200


def test_not_in_bank_dm(clear_reg, add_u1, add_u2):
    u2 = add_u2['auth_user_id']

    token1 = add_u1['token']
    token2 = add_u2['token']

    dm_id = create_dm(token1, [u2])

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = "/wordle oogaa"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code


def test_not_guessed_dm(clear_reg, add_u1, add_u2):
    u2 = add_u2['auth_user_id']

    token1 = add_u1['token']
    token2 = add_u2['token']

    dm_id = create_dm(token1, [u2])

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200
    msg = "/wordle OOGABOOGA"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200
    msg = "/wordle hello"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

    msg = "/wordle end"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == InputError.code

    msg = "/wordle start"
    ans = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                               'dm_id': dm_id, 'message': msg})
    assert ans.status_code == 200

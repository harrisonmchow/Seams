import jwt
import pytest
from src.other import SECRET, encode_token
from src.error import InputError, AccessError

from jwt import decode
from src.data_store import data_store

import requests
from src.config import url
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
# _________________________________________________________________________________________________________________-


def test_inv_u_id(clear_reg, add_u1):
    token1 = add_u1['token']
    u_id = 10
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.status_code == InputError.code


def test_solitary_global(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    u_id = add_u1['auth_user_id']
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.status_code == InputError.code


def test_not_global(clear_reg, add_u1, add_u2):
    token2 = add_u2['token']
    u_id = add_u1['auth_user_id']
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token2, "u_id": u_id})
    assert response.status_code == AccessError.code


def test_inv_token(clear_reg, add_u2):
    token1 = 55
    u_id = add_u2['auth_user_id']
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.status_code == AccessError.code


def test_inv_auth(clear_reg, add_u2):
    token1 = encode_token(-1)
    u_id = add_u2['auth_user_id']
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.status_code == AccessError.code


def test_pass(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    u_id = add_u2['auth_user_id']
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.json() == {}


def test_no_show_ch(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    u_id = add_u2['auth_user_id']
    token2 = add_u2['token']

    ch_id = add_ch(token1, 'Test_channel', True)['channel_id']
    print(f"CHID IN TEST: {ch_id}")
    print(f"tYPE: {type(ch_id)}")

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token2, "channel_id": ch_id})
    assert response.status_code == 200

    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.json() == {}

    out = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": token1, "channel_id": ch_id}).json()

    '''out = requests.get(
        f"{BASE_URL}/channel/details/v2", {"token": token1, "channel_id": ch_id}).json()
    out = requests.get(
        f"{BASE_URL}/channel/details/v2", {"token": token1, "channel_id": ch_id}).json()'''

    print(f"OUT IN REMOVE CH OWN TEST: {out}")

    assert out == {
        'name': 'Test_channel',
        'is_public': True,
        'owner_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'first',
          'name_last': 'last',
          'handle_str': 'firstlast', 'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}],
        'all_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'first',
          'name_last': 'last',
          'handle_str': 'firstlast', 'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}

# ______________________________________________________________________________


def test_no_show_ch_own(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    u_id = add_u2['auth_user_id']
    token2 = add_u2['token']

    ch_id = add_ch(token2, 'Test_channel', True)['channel_id']
    add_ch(token1, 'Test2_channel', True)['channel_id']
    print(f"CHID IN TEST: {ch_id}")
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token1, "channel_id": ch_id})
    assert response.status_code == 200

    out = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": token1, "channel_id": ch_id}).json()
    print(f"OUT HEREIN REMOVE: {out}")
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.json() == {}

    out = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": token1, "channel_id": ch_id}).json()
    print(f"OUT IN REMOVE CH OWN TEST: {out}")

    assert out == {
        'name': 'Test_channel',
        'is_public': True,
        'owner_members': [],
        'all_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'first',
          'name_last': 'last',
          'handle_str': 'firstlast', 'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}
# ___________________________________________________________________________________________


def test_user_profile(clear_reg, add_u1, add_u2, add_u3):
    token1 = add_u1['token']
    u_id = add_u2['auth_user_id']

    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.json() == {}

    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.json() == {}

    response = requests.get(f"{BASE_URL}/user/profile/v1",
                            params={"token": token1, "u_id": u_id})

    assert response.json() == {
        "user": {
            "u_id": 2,
            "email": "email2@gmail.com",
            "name_first": "Removed",
            "name_last": "user",
            "handle_str": "firsttwolasttwo", 'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'
        }
    }


def test_users_all(clear_reg, add_u1, add_u2, add_u3):
    token1 = add_u1['token']
    u_id = add_u2['auth_user_id']

    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": u_id})
    assert response.json() == {}

    response = requests.get(f"{BASE_URL}/users/all/v1",  # WRONG________________________
                            params={"token": token1})
    print(response.json())
    assert response.json() == {"users":
                               [{'u_id': 1,
                                 'email': 'email1@gmail.com',
                                 'name_first': 'first',
                                 'name_last': 'last',
                                 'handle_str': 'firstlast',
                                 'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
                                {
                                'u_id': 3,
                                'email': 'email3@gmail.com',
                                'name_first': 'firstthree',
                                'name_last': 'lastthree',
                                'handle_str': 'firstthreelastthree',
                                'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}


def create_dm(token, u_ids):
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token,
                                                               "u_ids": u_ids})
    assert response.status_code == 200
    dm_id = response.json()['dm_id']
    return dm_id


def test_remove_from_dms(clear_reg, add_u1, add_u2, add_u3):
    token1 = add_u1['token']
    id3 = add_u3['auth_user_id']
    id2 = add_u2['auth_user_id']
    create_dm(token1, [id2, id3])

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': token1, 'dm_id': 1})
    assert response.status_code == 200

    assert response.json() == {'name': 'firstlast, firstthreelastthree, firsttwolasttwo',
                               'members': [{'u_id': 2,
                                            'email': 'email2@gmail.com',
                                            'name_first': 'firsttwo',
                                            'name_last': 'lasttwo',
                                            'handle_str': 'firsttwolasttwo',
                                            'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
                                           {'u_id': 3,
                                            'email': 'email3@gmail.com',
                                            'name_first': 'firstthree',
                                            'name_last': 'lastthree',
                                            'handle_str': 'firstthreelastthree',
                                            'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
                                           {'u_id': 1,
                                            'email': 'email1@gmail.com',
                                            'name_first': 'first',
                                            'name_last': 'last',
                                            'handle_str': 'firstlast',
                                            'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}

    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": id2})
    assert response.status_code == 200
    assert response.json() == {}

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': token1, 'dm_id': 1})
    assert response.status_code == 200
    print(response.json())

    assert response.json() == {'name': 'firstlast, firstthreelastthree, firsttwolasttwo',
                               'members': [{'u_id': 3,
                                            'email': 'email3@gmail.com',
                                            'name_first': 'firstthree',
                                            'name_last': 'lastthree',
                                            'handle_str': 'firstthreelastthree',
                                            'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
                                           {'u_id': 1,
                                            'email': 'email1@gmail.com',
                                            'name_first': 'first',
                                            'name_last': 'last',
                                            'handle_str': 'firstlast',
                                            'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}


def test_user_remove_messages(clear_reg, add_u1, add_u2):
    token = add_u1['token']
    data = add_u2
    token2 = data['token']
    id2 = data['auth_user_id']
    # create a channel and then join it
    name = "Channel 1"
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": True})
    assert response_input.status_code == 200
    ch_id = response_input.json()['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token2, "channel_id": ch_id})

    # user 1 sends a message to the channel
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": ch_id, "message": "This is the first message to the channel"})
    assert response_input.status_code == 200
    # user 2 sends a message to the channel
    message = "Hi my name Jeff"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token2,
                                                                        "channel_id": ch_id, "message": message})
    assert response_input.status_code == 200
    # check it sent correctly
    response = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token,
                                                                       "channel_id": ch_id, "start": 0})

    assert response.status_code == 200
    data = response.json()
    assert data['messages'][0]['message_id'] == 2
    assert data['messages'][0]['u_id'] == id2
    assert data['messages'][0]['message'] == message

    # remove the user
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token, "u_id": id2})
    assert response.status_code == 200

    # check the message they sent earlier has been changed.
    response2 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token,
                                                                        "channel_id": ch_id, "start": 0})

    assert response2.status_code == 200
    data = response2.json()
    assert data['messages'][0]['message_id'] == 2
    assert data['messages'][0]['u_id'] == id2
    assert data['messages'][0]['message'] == "Removed user"


def test_remove_user_in_dms(clear_reg, add_u1, add_u2, add_u3):
    data = add_u1
    token1 = data['token']
    id1 = data['auth_user_id']
    data2 = add_u2
    token2 = data2['token']
    id2 = data2['auth_user_id']

    id3 = add_u3['auth_user_id']

    # create dm
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token1,
                                                               "u_ids": [id3, id2]})
    assert response.status_code == 200
    dm_id1 = response.json()['dm_id']

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token1,
                                                               "u_ids": [id3]})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token2,
                                                               "u_ids": [id3, id1]})
    assert response.status_code == 200
    dm_id2 = response.json()['dm_id']

    # remove the user
    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": id2})
    assert response.status_code == 200
    # look at details of dm1
    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': token1,
                                    'dm_id': dm_id1})
    assert response.status_code == 200
    dm_detail1 = response.json()

    in_dm1 = False
    for member in dm_detail1['members']:
        if member['u_id'] == id2:
            in_dm1 = True

    assert in_dm1 == False

    # look at details of dm2
    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': token1,
                                    'dm_id': dm_id2})
    assert response.status_code == 200
    dm_detail2 = response.json()
    in_dm2 = False
    for member in dm_detail2['members']:
        if member['u_id'] == id2:
            in_dm2 = True

    assert in_dm2 == False


def test_logout_after_remove(clear_reg, add_u1, add_u2):
    token1 = add_u1['token']
    id2 = add_u2['auth_user_id']
    tok2 = add_u2['token']

    response = requests.delete(
        f"{BASE_URL}/admin/user/remove/v1", json={"token": token1, "u_id": id2})
    assert response.status_code == 200
    response = requests.post(
        f"{BASE_URL}/auth/logout/v1", json={"token": tok2})

    assert response.status_code == AccessError.code

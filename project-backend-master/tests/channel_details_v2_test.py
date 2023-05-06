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

    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id})
    assert response.status_code == InputError.code


def test_not_authorised(clear_reg, add_u1, add_u2):
    # AccessError
    u1_token = add_u1['token']
    u2_token = add_u2['token']
    ch_id = add_ch_1(u1_token, "channel1", False)['channel_id']

    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u2_token, "channel_id": ch_id})

    assert response.status_code == AccessError.code


def test_no_ch_http(clear_reg, add_u1):
    '''Testing an invalid channel that doesnt exist with user existing'''
    u1_token = add_u1['token']
    ch_id = 10
    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id})
    assert response.status_code == InputError.code


def test_invalid_index_http(clear_reg, add_u1):
    ''' Testing invalid channel for a channel out of the index'''
    u1_token = add_u1['token']
    add_ch_1(u1_token, 'test-channel', True)
    ch_id = 3
    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id})
    assert response.status_code == InputError.code


def test_not_authorised_http(clear_reg, add_u1, add_u2):
    '''Testing when the channel ID is valid, but user
    is not a member of the channel'''
    u1_token = add_u1['token']
    u2_token = add_u2['token']
    ch = add_ch_1(u1_token, 'Test_channel', False)
    ch_id = ch['channel_id']
    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u2_token, "channel_id": ch_id})
    assert response.status_code == AccessError.code


def test_output_type_http(clear_reg, add_u1, add_u2):
    ''' Testing the output type as per the spec'''
    u1_token = add_u1['token']
    u2_token = add_u2['token']
    ch_id = add_ch_1(u1_token, 'Test_channel', True)['channel_id']
    requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": u2_token, "channel_id": ch_id})

    out = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id}).json()

    assert isinstance(out, dict) is True
    assert isinstance(out['name'], str) is True
    assert isinstance(out['is_public'], bool) is True
    assert isinstance(out['owner_members'], list) is True
    assert isinstance(out['all_members'], list) is True
    assert isinstance(out['owner_members'][0], dict) is True
    assert isinstance(out['all_members'][0], dict) is True
    assert isinstance(out['all_members'][1], dict) is True


def test_output_correct_http(clear_reg, add_u1, add_u2):
    '''Testing that the output is correct as per spec'''
    u1_token = add_u1['token']
    u2_id = add_u2['auth_user_id']

    ch_id = add_ch_1(u1_token, 'Test_channel', True)['channel_id']
    requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": u1_token, "channel_id": ch_id, "u_id": u2_id})

    out = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id}).json()

    assert out == {
        'name': 'Test_channel',
        'is_public': True,
        'owner_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'first',
          'name_last': 'last',
          'handle_str': 'firstlast',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}],
        'all_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'first',
          'name_last': 'last',
          'handle_str': 'firstlast',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
         {'u_id': 2,
         'email': 'email2@gmail.com',
          'name_first': 'firsttwo',
          'name_last': 'lasttwo',
          'handle_str': 'firsttwolasttwo',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}

    # It1 fixes


def test_invalid_auth_http(clear_reg, add_u1):
    ''' T'''
    u1_token = add_u1['token']
    u2_token = encode_token(10)
    ch_id = add_ch_1(u1_token, 'Test_channel', True)['channel_id']

    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u2_token, "channel_id": ch_id})
    assert response.status_code == AccessError.code


def test_invalid_auth2_http(clear_reg, add_u1):
    ''' T'''
    u1_token = add_u1['token']
    u2_token = encode_token(-1)
    ch_id = add_ch_1(u1_token, 'Test_channel', True)['channel_id']

    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u2_token, "channel_id": ch_id})
    assert response.status_code == AccessError.code


def test_invalid_tok_http(clear_reg, add_u1):
    ''' T'''
    u1_token = add_u1['token']
    u2_token = 10
    ch_id = add_ch_1(u1_token, 'Test_channel', True)['channel_id']

    response = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u2_token, "channel_id": ch_id})
    assert response.status_code == AccessError.code


# def test_global_details_http(clear_reg, add_u1, add_u2):

#     u1_token = add_u1['token']
#     u2_token = add_u2['token']
#     ch_id = add_ch_1(u2_token, 'Test_channel', False)[
#         'channel_id']  # private made by 2

#     out = requests.get(
#         f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id}).json()
#     print(out)
#     assert out == {
#         'name': 'Test_channel',
#         'is_public': False,
#         'owner_members':
#         [{'u_id': 2,
#          'email': 'email2@gmail.com',
#           'name_first': 'firsttwo',
#           'name_last': 'lasttwo',
#           'handle_str': 'firsttwolasttwo',
#           'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}],
#         'all_members':
#         [{'u_id': 2,
#          'email': 'email2@gmail.com',
#           'name_first': 'firsttwo',
#           'name_last': 'lasttwo',
#           'handle_str': 'firsttwolasttwo',
#           'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}


def test_output_correct_http2(clear_reg, add_u1, add_u2):
    '''Testing that the output is correct as per spec'''
    u1_token = add_u1['token']
    u2_token = add_u2['token']
    u1_id = add_u1['auth_user_id']

    ch_id = add_ch_1(u2_token, 'Test_channel', True)['channel_id']
    requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": u2_token, "channel_id": ch_id, "u_id": u1_id})

    out = requests.get(
        f"{BASE_URL}/channel/details/v2", params={"token": u1_token, "channel_id": ch_id}).json()

    assert out == {
        'name': 'Test_channel',
        'is_public': True,
        'owner_members':
        [{'u_id': 2,
         'email': 'email2@gmail.com',
          'name_first': 'firsttwo',
          'name_last': 'lasttwo',
          'handle_str': 'firsttwolasttwo',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}],
        'all_members':
        [{'u_id': 2,
         'email': 'email2@gmail.com',
          'name_first': 'firsttwo',
          'name_last': 'lasttwo',
          'handle_str': 'firsttwolasttwo',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
         {'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'first',
          'name_last': 'last',
          'handle_str': 'firstlast',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}

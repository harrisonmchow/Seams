'''
This test file aims to validate the functionaility of channels/listall/v2 and the front end. 

Functions:
    clear
    register_and_login1
    register_and_login2
    create_channel

    test_invalid_user
    test_invalid_token
    test_no_channels
    test_one_channel_public
    test_one_channel_private
    test_multiple_channels
    test_return_types
'''

import pytest
import requests
from src.error import InputError, AccessError
from src.config import url
from src.other import encode_token
BASE_URL = url


@pytest.fixture
def clear():
    '''
    clear the datastore
    '''
    print(f"Clearing. Running: {BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200


def register_and_login1():
    '''
    register and login a user
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200

    data = response.json()
    token = data['token']
    return token


def register_and_login2():
    '''
    register and login a user
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                   "password": "passworD1234655", "name_first": "James", "name_last": "Bob"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    return token


def create_channel(token, name, is_public):
    '''
    create a channel
    '''
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": is_public})
    assert response_input.status_code == 200
    channel_id = response_input.json()
    return channel_id

# --------------------------------------------------------------------------------------------------


def test_invalid_user(clear):
    '''
    call channels list all with an invalid user id
    '''
    invalid_auth_id = -1
    invalid_token = encode_token(invalid_auth_id)
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": invalid_token})
    assert response_input.status_code == AccessError.code


def test_invalid_token(clear):
    '''
    call channels list all with an invalid token format
    '''
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": -1})
    assert response_input.status_code == AccessError.code


def test_no_channels(clear):
    '''
    call channels list all when there are no channels
    '''
    token1 = register_and_login1()
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token1})  # json={"token": token1}
    assert response_input.status_code == 200
    data = response_input.json()
    assert data['channels'] == []


def test_one_channel_public(clear):
    '''
    call channels list all with one public channel
    '''
    token = register_and_login1()
    name = "Channel 1"

    channel_id = create_channel(token, name, True)
    expected = {"channel_id": channel_id['channel_id'], "name": name}
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": token})
    assert response_input.status_code == 200
    channels_recieved = response_input.json()
    assert expected in channels_recieved['channels']


def test_one_channel_private(clear):
    '''
    call channels list all with one private channel
    '''
    token = register_and_login1()
    name = "Channel 1"

    channel_id = create_channel(token, name, False)
    expected = {"channel_id": channel_id['channel_id'], "name": name}
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": token})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()

    assert expected in channel_recieved['channels']


def test_multiple_channels(clear):
    '''
    call channels list all when there are multiple channels
    '''
    token1 = register_and_login1()
    token2 = register_and_login2()

    name1 = "Channel 1"
    channel_id1 = create_channel(token1, name1, False)
    name2 = "Channel 1"
    channel_id2 = create_channel(token1, name2, True)

    expected = [{"channel_id": channel_id1['channel_id'], "name": name1},
                {"channel_id": channel_id2['channel_id'], "name": name2}]

    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": token2})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()

    assert expected == channel_recieved['channels']
    assert len(channel_recieved['channels']) == 2


def test_return_type(clear):
    '''
    test the return type of channels list all
    '''
    token = register_and_login1()
    name = "Channel 1"

    create_channel(token, name, False)
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": token})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()

    assert isinstance(channel_recieved['channels'][0]['name'], str) == True
    assert isinstance(
        channel_recieved['channels'][0]['channel_id'], int) == True

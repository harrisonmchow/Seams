'''
This test file aims to validate the functionaility of channels/list/v2 and the front end. 

Functions:
    clear
    register_and_login
    create_channel

    invalid_user
    no_channels
    one_channel_public
    one_channel_private
    multiple_channels
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
    clear the data store
    '''
    print(f"Clearing. Running: {BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200


@pytest.fixture
def register_and_login():
    '''
    register and login a user
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    return token


@pytest.fixture
def register_and_login2():
    '''
    register and login a user
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "james", "name_last": "dylan"})
    assert response.status_code == 200

    response2 = requests.post(f"{BASE_URL}/auth/login/v2", json={"email": "james@unsw.edu.au",
                                                                 "password": "Password12345"})
    assert response2.status_code == 200
    data = response2.json()
    token = data['token']
    return token


def create_channel(token, name, is_public):
    '''
    create channel
    '''
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": is_public})
    assert response_input.status_code == 200

    channel_id = response_input.json()
    return channel_id


# --------------------------------------------------------------------------------------------------

def test_invalid_user(clear):
    '''
    try call channels list using an invalid user id
    '''
    invalid_user = -1
    invalid_token = encode_token(invalid_user)
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": invalid_token})
    assert response_input.status_code == AccessError.code


def test_invalid_token(clear):
    '''
    try call channels list using an invalid token format
    '''
    invalid_token = -1
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": invalid_token})
    assert response_input.status_code == AccessError.code


def test_no_channels(clear, register_and_login):
    '''
    call channels list when there are no channels. Should be empty
    '''
    token1 = register_and_login
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token1})
    assert response_input.status_code == 200
    channels = response_input.json()
    assert channels['channels'] == []


def test_one_channel_public(clear, register_and_login):
    '''
    call channels list when there are is a public channel.
    '''
    token = register_and_login
    name = "Channel 1"

    channel_id = create_channel(token, name, True)
    expected = {"channel_id": channel_id['channel_id'], "name": name}
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()
    assert expected in channel_recieved['channels']


def test_one_channel_private(clear, register_and_login):
    '''
    call channels list when there is a private channel.
    '''

    token = register_and_login
    name = "Channel 1"

    channel_id = create_channel(token, name, False)
    expected = {"channel_id": channel_id['channel_id'], "name": name}
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()
    assert expected in channel_recieved['channels']


def test_multiple_channels(clear, register_and_login):
    '''
    call channels list when there are multiple channels to a user
    '''
    token = register_and_login

    name1 = "Channel 1"
    channel_id1 = create_channel(token, name1, False)
    name2 = "Channel 1"
    channel_id2 = create_channel(token, name2, True)

    expected = [{"channel_id": channel_id1['channel_id'], "name": name1},
                {"channel_id": channel_id2['channel_id'], "name": name2}]

    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()

    assert expected == channel_recieved['channels']
    assert len(channel_recieved['channels']) == 2


def test_in_one_channel(clear, register_and_login, register_and_login2):
    '''
    two users create their own channels then both call channels list
    '''
    token = register_and_login
    name1 = "Channel 1"
    channel_id1 = create_channel(token, name1, False)

    token2 = register_and_login2
    name2 = "Channel 1"
    channel_id2 = create_channel(token2, name2, True)
    expected1 = [{"channel_id": channel_id1['channel_id'], "name": name1}]
    expected2 = [{"channel_id": channel_id2['channel_id'], "name": name2}]
    response1 = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response1.status_code == 200
    data1 = response1.json()
    assert expected1 == data1['channels']

    response2 = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token2})
    assert response2.status_code == 200
    data2 = response2.json()
    assert expected2 == data2['channels']


def test_return_types(clear, register_and_login):
    '''
    call channels list and check the return types of the data.
    '''
    token = register_and_login
    name = "Channel 1"

    create_channel(token, name, True)
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response_input.status_code == 200
    channel_recieved = response_input.json()
    assert isinstance(
        channel_recieved['channels'][0]['channel_id'], int) == True
    assert isinstance(channel_recieved['channels'][0]['name'], str) == True

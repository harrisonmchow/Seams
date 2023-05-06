'''
This test file aims to validate the functionaility of channels/create/v2 and the front end. 

Functions:
    invalid_name_too_short
    invalid_name_too_long
    invalid_token_creating_channel
    create_singular_channel_public
    create_singular_channel_private
    test_return_types
'''

from code import InteractiveConsole
import pytest
import requests
from src.error import InputError, AccessError
from src.config import url
from src.other import encode_token
BASE_URL = url


@pytest.fixture
def clear_and_register():
    '''
    clear the data store and register a user
    '''

    print(f"Clearing. Running: {BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

    response2 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                    "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response2.status_code == 200

    data = response2.json()
    token = data['token']
    return token


def log_in():
    '''
    login a user
    '''
    response2 = requests.post(f"{BASE_URL}/auth/login/v2", json={"email": "harry@unsw.edu.au",
                                                                 "password": "Password12345"})
    assert response2.status_code == 200

    data = response2.json()
    token = data['token']
    return token

# -------------------------------------------------------------------------------------------


def test_invalid_name_too_short(clear_and_register):
    '''
    try create a channel with no name. This should raise an error
    '''
    clear_and_register
    token = log_in()
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": "", "is_public": True})
    assert response_input.status_code == InputError.code


def test_invalid_name_too_long(clear_and_register):
    '''
    try create a channel with too long of a name. This should raise an error
    '''
    clear_and_register
    token = log_in()
    name_too_long = "ThisChannelNameIsTooLong"
    assert len(name_too_long) > 20
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name_too_long, "is_public": True})
    assert response_input.status_code == InputError.code


def test_invalid_token_creating_channel(clear_and_register):
    '''
    try create a channel with an invalid token. This should raise an error
    '''
    clear_and_register
    invalid_auth_id = -1
    invalid_token = encode_token(invalid_auth_id)
    response_input = requests.post(f"{BASE_URL}/channels/create/v2",
                                   json={"token": invalid_token, "name": "Channel 1", "is_public": True})
    assert response_input.status_code == AccessError.code


def test_invalid_token2_creating_channel(clear_and_register):
    '''
    try create a channel with an invalid token format. This should raise an error
    '''
    clear_and_register
    response_input = requests.post(f"{BASE_URL}/channels/create/v2",
                                   json={"token": -1, "name": "Channel 1", "is_public": True})
    assert response_input.status_code == AccessError.code


def test_create_singular_channel_public(clear_and_register):
    '''
    create a public channel
    '''
    clear_and_register
    token = log_in()

    name = "Channel 1"
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": True})
    assert response_input.status_code == 200

    channel_id_create = response_input.json()
    channel = {"channel_id": channel_id_create["channel_id"], "name": name}

    response_input2 = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response_input2.status_code == 200
    channels = response_input2.json()

    assert channel in channels['channels']


def test_create_singular_channel_private(clear_and_register):
    '''
    create a private channel
    '''
    clear_and_register
    token = log_in()

    name = "Channel 1"
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": False})
    assert response_input.status_code == 200

    channel_id_create = response_input.json()
    channel = {"channel_id": channel_id_create["channel_id"], "name": name}

    response_input2 = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": token})
    assert response_input2.status_code == 200
    channels = response_input2.json()

    assert channel in channels['channels']


def test_return_types(clear_and_register):
    '''
    create a channel, then confirm the types stored in the data store.
    '''
    clear_and_register
    token = log_in()
    name = "Channel 1"
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": False})
    assert response_input.status_code == 200

    channel_created = response_input.json()
    assert isinstance(channel_created['channel_id'], int)

    response = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['channels'][0]['name'], str) == True
    assert isinstance(data['channels'][0]['channel_id'], int) == True

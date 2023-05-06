'''
This test fle aims to validate the functionality of the channels_create_v1
function using pytest.

Functions:
    clear_and_register_users()
    test_channels_create_invalid_too_short1
    test_channels_create_invalid_too_short2
    test_channels_create_invalid_too_long1
    test_channels_create_invalid_too_long2
    test_channels_create_invalid_auth
    test_channels_create_valid_public
    test_channels_create_public_and_private
    
'''
import pytest
from src.auth import auth_register_v2
from src.channel import channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1
from src.error import InputError, AccessError
from src.other import clear_v1, encode_token
import requests
from src.config import url
BASE_URL = url


@pytest.fixture
def clear_and_register_users():
    '''
    Fixture that clears data store and then registers a user, returning their id.
    '''
    clear_v1()
    user_id1 = auth_register_v2(
        "harry@unsw.edu.au", "Password123", "harry", "chow")
    user_id2 = auth_register_v2(
        "jack@unsw.edu.au", "Comp1531iseasy", "jack", "adams")
    return user_id1, user_id2


def test_channels_create_invalid_too_short1(clear_and_register_users):
    '''
    Invalid Name --> Too short. This test should fail
    '''

    user_id = clear_and_register_users[0]
    with pytest.raises(InputError):
        channels_create_v1(user_id['auth_user_id'], "", True)


def test_channels_create_invalid_too_short2(clear_and_register_users):
    '''
    Invalid Name --> Too short. This test should fail
    '''

    user_id = clear_and_register_users[0]
    with pytest.raises(InputError):
        channels_create_v1(user_id['auth_user_id'], "", False)


def test_channels_create_invalid_too_long1(clear_and_register_users):
    '''
    Invalid Name --> Too long. This test should fail
    '''

    user_id = clear_and_register_users[0]
    with pytest.raises(InputError):
        channels_create_v1(user_id['auth_user_id'],
                           "HarryJamesG3rardJackF", True)


def test_channels_create_invalid_too_long2(clear_and_register_users):
    '''
    Invalid Name --> Too long. This test should fail
    '''

    user_id = clear_and_register_users[0]
    with pytest.raises(InputError):
        channels_create_v1(user_id['auth_user_id'],
                           "F3lixjamesharryjackge", False)


def test_channels_create_invalid_token():
    '''
    A non authenticated user tries to create a channel, creating an AccessError
    '''
    clear_v1()
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", 
        json={"token": -1, "name": "F3lixjamesharryjackge", "is_public": False})
    assert response_input.status_code == AccessError.code

def test_channels_create_invalid_auth():
    '''
    A non authenticated user tries to create a channel, creating an AccessError
    '''
    clear_v1()
    invalid_token = encode_token(-1)
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", 
        json={"token": invalid_token, "name": "F3lixjamesharryjackge", "is_public": False})
    assert response_input.status_code == AccessError.code
    


def test_channels_create_valid_public(clear_and_register_users):
    '''
    Valid test. This should pass. Register two users, one of which creates a
    public channel and the other joins it.
    '''

    user_id1, user_id2 = clear_and_register_users

    # Create a channel and have another user join it
    ch_id = channels_create_v1(user_id1['auth_user_id'], "Channel_1", True)
    channel_join_v1(user_id2['auth_user_id'], ch_id['channel_id'])
    # Check that the channel was created successfully and that they are both in it
    assert channels_list_v1(user_id1['auth_user_id']) == \
        channels_list_v1(user_id2['auth_user_id'])


def test_channels_create_public_and_private(clear_and_register_users):
    '''
    Valid test. This should pass. Register two users, both of which create their own channels.
    Confirm that 2 channels were in fact created.
    '''

    user_id1, user_id2 = clear_and_register_users

    # Create two channels, one private and one public
    ch_id1 = channels_create_v1(user_id1['auth_user_id'], "Channel_1", True)
    ch_id2 = channels_create_v1(user_id2['auth_user_id'], "Channel_2", False)
    channel_join_v1(user_id2['auth_user_id'], ch_id1['channel_id'])
    channel_invite_v1(user_id2['auth_user_id'],
                      ch_id2['channel_id'], user_id1['auth_user_id'])

    # Check that two channels were actually created
    assert channels_listall_v1(user_id1['auth_user_id']) == \
        channels_listall_v1(user_id2['auth_user_id'])

'''
This test fle aims to validate the functionality of the channels_listall_v1
function using pytest.

Functions:
    clear_and_register_users
    test_channels_listall_invalid_token
    test_channels_listall_invalid_auth
    test_channels_listall_empty
    test_channels_listall_private
    test_channels_listall_both_private_and_public
    test_channels_listall_both_private_invite
'''
from base64 import encode
import pytest
from src.auth import auth_register_v2
from src.channel import channel_invite_v1, channel_join_v1
from src.channels import channels_listall_v1, channels_create_v1
from src.other import clear_v1, encode_token
from src.error import AccessError
import requests
from src.config import url
BASE_URL = url


@pytest.fixture
def clear_and_register_users():
    '''
    Fixture that clears data store and then registers two users, returning their ids.
    '''
    clear_v1()
    user_id1 = auth_register_v2(
        "harry@unsw.edu.au", "Password123", "harry", "chow")
    user_id2 = auth_register_v2(
        "jack@unsw.edu.au", "Comp1531iseasy", "jack", "adams")

    return user_id1, user_id2


def test_channels_listall_invalid_token():
    '''
    A non authenticated user tries to create a channel, creating an AccessError
    '''
    clear_v1()
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": -1})
    assert response_input.status_code == AccessError.code
    # with pytest.raises(AccessError):
    #     channels_listall_v1(-1)


def test_channels_listall_invalid_auth():
    '''
    A non authenticated user tries to create a channel, creating an AccessError
    '''
    clear_v1()
    invalid_token = encode_token(-1)
    response_input = requests.get(
        f"{BASE_URL}/channels/listall/v2", params={"token": invalid_token})
    assert response_input.status_code == AccessError.code
    # with pytest.raises(AccessError):
    #     channels_listall_v1(-1)


def test_channels_listall_empty(clear_and_register_users):
    '''
    Register two users but don't create any channels.
    Hence, channels_listall_v1 should return an empty list.
    '''

    user_id1, user_id2 = clear_and_register_users

    assert channels_listall_v1(user_id1['auth_user_id']) == {'channels': []}
    assert channels_listall_v1(user_id2['auth_user_id']) == {'channels': []}


def test_channels_listall_private(clear_and_register_users):
    '''
    Register two users, each of which creates a private channel.
    Verify that channels_listall_v1 returns their private channels.
    '''
    user_id1, user_id2 = clear_and_register_users

    ch_id1 = channels_create_v1(user_id1['auth_user_id'], "Channel 1", False)
    ch_id2 = channels_create_v1(user_id2['auth_user_id'], "Channel 2", False)

    # It should be in the same order they were created in
    assert channels_listall_v1(user_id1['auth_user_id']) == \
        {'channels': [{'channel_id': ch_id1['channel_id'], 'name': 'Channel 1'},
                      {'channel_id': ch_id2['channel_id'], 'name': 'Channel 2'}]}
    assert channels_listall_v1(user_id2['auth_user_id']) == \
        {'channels': [{'channel_id': ch_id1['channel_id'], 'name': 'Channel 1'},
                      {'channel_id': ch_id2['channel_id'], 'name': 'Channel 2'}]}

    assert channels_listall_v1(user_id1['auth_user_id']) == channels_listall_v1(
        user_id2['auth_user_id'])


def test_channels_listall_both_private_and_public(clear_and_register_users):
    '''
    Register two users. One of them creates a public and private channel.
    channels_listall_v1() should still return both channels, for both users. 
    '''

    user_id1, user_id2 = clear_and_register_users

    ch_id1 = channels_create_v1(user_id1['auth_user_id'], "Channel 1", True)
    ch_id2 = channels_create_v1(user_id1['auth_user_id'], "Channel 2", False)

    # It should be in the same order they were created in
    assert channels_listall_v1(user_id1['auth_user_id']) == {'channels':
                                                             [{'channel_id': ch_id1['channel_id'], 'name': 'Channel 1'},
                                                              {'channel_id': ch_id2['channel_id'], 'name': 'Channel 2'}]}

    assert channels_listall_v1(user_id2['auth_user_id']) == {'channels':
                                                             [{'channel_id': ch_id1['channel_id'], 'name': 'Channel 1'},
                                                              {'channel_id': ch_id2['channel_id'], 'name': 'Channel 2'}]}

    assert channels_listall_v1(user_id1['auth_user_id']) == \
        channels_listall_v1(user_id2['auth_user_id'])


def test_channels_listall_multiple_not_shared(clear_and_register_users):
    '''
    Register two users, who both create their own channels, then invite the other user.
    When channels_listall_v1 is run on both of them, they should have the same channels.
    '''

    user_id1, user_id2 = clear_and_register_users

    name_1 = "Channel 1"
    name_2 = "Channel 2"
    name_3 = "Channel 3"
    name_4 = "Channel 4"

    ch_id1 = channels_create_v1(user_id1['auth_user_id'], name_1, False)
    ch_id2 = channels_create_v1(user_id2['auth_user_id'], name_2, True)
    ch_id3 = channels_create_v1(user_id2['auth_user_id'], name_3, True)
    ch_id4 = channels_create_v1(user_id2['auth_user_id'], name_4, False)

    assert channels_listall_v1(user_id1['auth_user_id']) == \
        channels_listall_v1(user_id2['auth_user_id'])

    # It should be in the same order they were created in
    assert channels_listall_v1(user_id1['auth_user_id']) == {'channels':
                                                             [{'channel_id': ch_id1['channel_id'], 'name': name_1},
                                                              {'channel_id': ch_id2['channel_id'], 'name': name_2},
                                                                 {'channel_id': ch_id3['channel_id'], 'name': name_3},
                                                                 {'channel_id': ch_id4['channel_id'], 'name': name_4}]}

# Replicate failed test functions


def test_channels_list_test1():
    clear_v1()
    email = 'sheriff.woody@andysroom.com'
    password = 'qazwsx!!'
    name_first = 'sheriff'
    name_last = 'woody'
    name1 = 'woodys toybox'
    id = auth_register_v2(email, password, name_first,
                          name_last)['auth_user_id']
    ch1 = channels_create_v1(id, name1, True)['channel_id']
    channel_detail = {'channel_id': ch1, 'name': name1}
    assert channel_detail in channels_listall_v1(id)['channels']


def test_channels_list_test2():
    clear_v1()
    email = 'sheriff.woody@andysroom.com'
    password = 'qazwsx!!'
    name_first = 'sheriff'
    name_last = 'woody'
    name1 = 'woodys toybox'
    name2 = 'zergs lair'
    id = auth_register_v2(email, password, name_first,
                          name_last)['auth_user_id']
    ch1 = channels_create_v1(id, name1, True)['channel_id']
    ch2 = channels_create_v1(id, name2, False)['channel_id']

    expected_chs = [
        {'channel_id': ch1, 'name': name1},
        {'channel_id': ch2, 'name': name2}
    ]
    chs = channels_listall_v1(id)['channels']
    assert expected_chs == chs

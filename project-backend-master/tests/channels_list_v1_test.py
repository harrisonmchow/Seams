'''
This test fle aims to validate the functionality of the channels_list_v1
function using pytest.

Functions:
    clear_and_register_users()
    test_channels_list_invalid_token
    test_channels_list_invalid_auth
    test_channels_list_empty()
    test_channels_list_private()
    test_channels_list_same_channels()
    test_channels_list_multiple_channels()
'''
from base64 import encode
import pytest
from src.auth import auth_register_v2
from src.channel import channel_join_v1, channel_invite_v1
from src.channels import channels_list_v1, channels_create_v1
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


def test_channels_list_invalid_token():
    '''
    A non authenticated user tries to create a channel, creating an AccessError
    '''
    clear_v1()
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": -1})
    assert response_input.status_code == AccessError.code


def test_channels_list_invalid_auth():
    '''
    A non authenticated user tries to create a channel, creating an AccessError
    '''
    clear_v1()
    #invalid_token = encode_token(-1)
    response_input = requests.get(
        f"{BASE_URL}/channels/list/v2", params={"token": -1})
    assert response_input.status_code == AccessError.code


def test_channels_list_empty(clear_and_register_users):
    '''
    Register two users but don't create any channels.
    Hence, channels_list_v1 should return an empty list.
    '''

    user_id1, user_id2 = clear_and_register_users
    assert channels_list_v1(user_id1['auth_user_id']) == {'channels': []}
    assert channels_list_v1(user_id2['auth_user_id']) == {'channels': []}
    assert channels_list_v1(user_id2['auth_user_id']) == channels_list_v1(
        user_id1['auth_user_id'])


def test_channels_list_private(clear_and_register_users):
    '''
    Register two users, each of which creates a private channel.
    It should still return the channels as expected
    '''

    user_id1, user_id2 = clear_and_register_users

    id1 = channels_create_v1(user_id1['auth_user_id'], "Channel 1", False)
    id2 = channels_create_v1(user_id2['auth_user_id'], "Channel 2", False)
    assert channels_list_v1(user_id1['auth_user_id']) == {'channels': [
        {'channel_id': id1['channel_id'], 'name': "Channel 1"}]}
    assert channels_list_v1(user_id2['auth_user_id']) == {'channels': [
        {'channel_id': id2['channel_id'], 'name': "Channel 2"}]}


def test_channels_list_public(clear_and_register_users):
    '''
    Register two users, each of which creates a public channel.
    It should still return the channels as expected
    '''

    user_id1, user_id2 = clear_and_register_users

    id1 = channels_create_v1(user_id1['auth_user_id'], "Channel 1", True)
    id2 = channels_create_v1(user_id2['auth_user_id'], "Channel 2", True)
    assert channels_list_v1(user_id1['auth_user_id']) == {'channels': [
        {'channel_id': id1['channel_id'], 'name': "Channel 1"}]}
    assert channels_list_v1(user_id2['auth_user_id']) == {'channels': [
        {'channel_id': id2['channel_id'], 'name': "Channel 2"}]}


def test_channels_list_same_channels(clear_and_register_users):
    '''
    Register two users, one of which creates a public channel, and the other joins said channel.
    Hence, channels_list_v1 will return the same output for both users.
    '''

    user_id1, user_id2 = clear_and_register_users

    ch_id = channels_create_v1(user_id1['auth_user_id'], "Channel 1", True)
    channel_join_v1(user_id2['auth_user_id'], ch_id['channel_id'])
    assert channels_list_v1(user_id1['auth_user_id']) == channels_list_v1(
        user_id2['auth_user_id'])


def test_channels_list_multiple_channels(clear_and_register_users):
    '''
    Register a user and create three channels. Verify that when channels_list_v1 is run,
    the 3 channels are in fact the ones we created.
    '''

    user_id = clear_and_register_users[0]
    name_1 = "Channel 1"
    name_2 = "Channel 2"
    name_3 = "Channel 3"
    ch_id1 = channels_create_v1(user_id['auth_user_id'], name_1, True)
    ch_id2 = channels_create_v1(user_id['auth_user_id'], name_2, True)
    ch_id3 = channels_create_v1(user_id['auth_user_id'], name_3, False)

    assert channels_list_v1(user_id['auth_user_id']) == {'channels': [{
        'channel_id': ch_id1['channel_id'], 'name': name_1},
        {'channel_id': ch_id2['channel_id'], 'name': name_2},
        {'channel_id': ch_id3['channel_id'], 'name': name_3}]}

# Replicating failed test functions


def test_channels_list_test1():
    clear_v1()
    email = 'sheriff.woody@andysroom.com'
    password = 'qazwsx!!'
    name_first = 'sheriff'
    name_last = 'woody'
    name = 'andy'
    id = auth_register_v2(email, password, name_first,
                          name_last)['auth_user_id']
    ch = channels_create_v1(id, name, True)['channel_id']

    deets = {'channel_id': ch, 'name': name}
    assert deets in channels_list_v1(id)['channels']


def test_channels_list_test2():
    clear_v1()

    email1 = 'sheriff.woody@andysroom.com'
    password1 = 'qazwsx!!'
    name_first1 = 'sheriff'
    name_last1 = 'woody'

    email2 = 'zerg.thedestroyer@zergworld.com'
    password2 = '!!qazwsx'
    name_first2 = 'lord'
    name_last2 = 'zerg'

    name = 'andy'

    id1 = auth_register_v2(email1, password1, name_first1, name_last1)[
        'auth_user_id']
    id2 = auth_register_v2(email2, password2, name_first2, name_last2)[
        'auth_user_id']
    ch = channels_create_v1(id1, name, False)['channel_id']
    channel_invite_v1(id1, ch, id2)
    channel_detail = {'channel_id': ch, 'name': name}
    assert channel_detail in channels_list_v1(id2)['channels']


def test_channels_list_test3():
    clear_v1()
    email = 'sheriff.woody@andysroom.com'
    password = 'qazwsx!!'
    name_first = 'sheriff'
    name_last = 'woody'
    name1 = 'andy'
    name2 = 'ZERG'
    is_public1 = False
    is_public2 = False
    id = auth_register_v2(email, password, name_first,
                          name_last)['auth_user_id']

    ch_1 = channels_create_v1(id, name1, is_public1)['channel_id']
    ch_2 = channels_create_v1(id, name2, is_public2)['channel_id']
    expected_joined = [{'channel_id': ch_1, 'name': name1},
                       {'channel_id': ch_2, 'name': name2}]
    joined = channels_list_v1(id)['channels']

    assert expected_joined == joined

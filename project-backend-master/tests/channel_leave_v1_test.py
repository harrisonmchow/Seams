'''
This test fle aims to validate the functionality of the channel_leave_v1
function using pytest.

Functions:
    clear_register_user_and_create_channel()
    clear_register_two_users_and_create_channel()
    test_valid_input()
    test_invalid_channel_id()
    test_user_not_member_of_channel()
    test_user_removed_from_channel()
    test_messages_remain()
    test_channel_remains_when_only_owner_leaves()
    test_correct_member_is_removed()
'''
import pytest
import requests
from src.error import InputError, AccessError
from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_user_and_create_channel():
    '''
    A fixture which clears the system, registers and logs
    in a user and then creates a channel which the user is a member of.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response1 = requests.post(f"{BASE_URL}/auth/register/v2",
                              json={"email": "john.smith@unsw.edu.au", "password": "password",
                                    "name_first": "John", "name_last": "Smith"})

    user = response1.json()

    response2 = requests.post(f"{BASE_URL}/channels/create/v2",
                              json={"token": user['token'], "name": "Badger Channel", "is_public": True})
    channel = response2.json()
    return user, channel


@pytest.fixture
def clear_register_two_users_and_create_channel():
    '''
    A fixture which clears the system, registers and logs
    in two users and then creates a channel which both users are a member of.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response1 = requests.post(f"{BASE_URL}/auth/register/v2",
                              json={"email": "john.smith@unsw.edu.au", "password": "password",
                                    "name_first": "John", "name_last": "Smith"})
    user_1 = response1.json()

    response2 = requests.post(f"{BASE_URL}/channels/create/v2",
                              json={"token": user_1['token'], "name": "Badger Channel", "is_public": True})
    channel = response2.json()

    response3 = requests.post(f"{BASE_URL}/auth/register/v2",
                              json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD",
                                    "name_first": "Will", "name_last": "Jones"})
    user_2 = response3.json()

    requests.post(f"{BASE_URL}/channel/join/v2",
                  json={"token": user_2["token"], "channel_id": channel["channel_id"]})

    return user_1, user_2, channel


def test_valid_input(clear_register_user_and_create_channel):
    '''
    Verifies that channel/leave/v1 returns a status code of 200 with valid input.
    '''
    user, channel = clear_register_user_and_create_channel
    response = requests.post(f"{BASE_URL}/channel/leave/v1",
                             json={"token": user['token'], "channel_id": channel['channel_id']})
    assert response.status_code == 200


def test_invalid_channel_id(clear_register_user_and_create_channel):
    '''
    Verifies that channel/leave/v1 returns an InputError when the user
    attemps to leave a channel which doesn't exist.
    '''
    user = clear_register_user_and_create_channel[0]
    channel_id = 5
    response = requests.post(f"{BASE_URL}/channel/leave/v1",
                             json={"token": user['token'], "channel_id": channel_id})
    assert response.status_code == InputError.code


def test_user_not_member_of_channel(clear_register_user_and_create_channel):
    '''
    Verifies that channel/leave/v1 returns an AccessError when the channel_id
    is valid, but the user is not a member of the channel.
    '''
    channel = clear_register_user_and_create_channel[1]

    response = requests.post(f'{BASE_URL}/auth/register/v2',
                             json={'email': 'lu.lu@niji.retired',
                                   'password': 'conlulu',
                                   'name_first': 'lu',
                                   'name_last': 'lu'})
    response = requests.post(f'{BASE_URL}/auth/login/v2',
                             json={'email': 'lu.lu@niji.retired',
                                   'password': 'conlulu'})
    assert response.status_code == 200
    user_new = response.json()

    response = requests.post(f"{BASE_URL}/channel/leave/v1",
                             json={"token": user_new['token'], "channel_id": channel['channel_id']})
    assert response.status_code == AccessError.code


def test_user_removed_from_channel(clear_register_user_and_create_channel):
    '''
    Verifies that channel/leave/v1 removes a member from the
    channel members list as required.
    '''
    user, channel = clear_register_user_and_create_channel
    requests.post(f"{BASE_URL}/channel/leave/v1",
                  json={"token": user['token'], "channel_id": channel['channel_id']})

    # Attempt to view messages from a channel which the user is no longer a member of
    start = 0
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'], "start": start})
    assert response.status_code == AccessError.code


def test_messages_remain(clear_register_two_users_and_create_channel):
    '''
    Verifies that channel/leave/v1 leaves the messages of
    the removed member in the channel.

    This is verified by having two users join a channel,
    having one send some messages and then leave, whilst
    the second user then tries to view the messages that the first user sent
    '''
    user_1, user_2, channel = clear_register_two_users_and_create_channel

    for send in range(0, 5):
        requests.post(f"{BASE_URL}/message/send/v1",
                      json={"token": user_1["token"], "channel_id": channel["channel_id"],
                            "message": f"message {send + 1}"})

    requests.post(f"{BASE_URL}/channel/leave/v1",
                  json={"token": user_1['token'], "channel_id": channel['channel_id']})

    start = 0
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user_2['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    response_data = response.json()

    most_recent_message = response_data['messages'][0]
    assert most_recent_message['message'] == "message 5"

    least_recent_message = response_data['messages'][4]
    assert least_recent_message['message'] == "message 1"


def test_channel_remains_when_only_owner_leaves(clear_register_user_and_create_channel):
    '''
    Verifies that if channel/leave/v1 removes the only owner
    of the channel, the channel will remain.
    '''
    user, channel = clear_register_user_and_create_channel

    requests.post(f"{BASE_URL}/channel/leave/v1",
                  json={"token": user['token'], "channel_id": channel['channel_id']})

    response = requests.get(f"{BASE_URL}/channels/listall/v2",
                            params={"token": user['token']})
    response_data = response.json()

    channel_1 = response_data['channels'][0]
    assert channel_1['name'] == "Badger Channel"


def test_correct_member_is_removed(clear_register_two_users_and_create_channel):
    '''
    Verifies that channel/leave/v1 removes only the one member who is leaving
    the channel, whilst a second member can still interact with the channel.
    '''
    user_1, user_2, channel = clear_register_two_users_and_create_channel

    requests.post(f"{BASE_URL}/channel/leave/v1",
                  json={"token": user_1['token'], "channel_id": channel['channel_id']})

    response = requests.get(f"{BASE_URL}/channel/details/v2",
                            params={"token": user_2['token'], "channel_id": channel['channel_id']})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/channel/details/v2",
                            params={"token": user_1['token'], "channel_id": channel['channel_id']})
    assert response.status_code == AccessError.code


def test_owner_removed_from_channel(clear_register_two_users_and_create_channel):
    '''
    Verifies that channel/leave/v1 removes an owner from both
    the member and owner list.
    '''
    user_1, user_2, channel = clear_register_two_users_and_create_channel

    requests.post(f'{BASE_URL}/channel/addowner/v1',
                  json={'token': user_1['token'], 'channel_id': channel['channel_id'],
                        'u_id': user_2['auth_user_id']})

    requests.post(f"{BASE_URL}/channel/leave/v1",
                  json={"token": user_2['token'], "channel_id": channel['channel_id']})

    # Attempt to view messages from a channel which the user is no longer a member of
    start = 0
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user_2['token'], "channel_id": channel['channel_id'], "start": start})
    assert response.status_code == AccessError.code


def test_global_owner_removed_from_channel(clear_register_two_users_and_create_channel):
    '''
    Verifies that channel/leave removes a global owner
    from the channel member list.
    '''
    user_1, user_2, channel = clear_register_two_users_and_create_channel

    p_id = 1
    requests.post(f"{BASE_URL}/admin/userpermission/change/v1",
                  json={"token": user_1['token'], "u_id": user_2, "permission_id": p_id})

    requests.post(f"{BASE_URL}/channel/leave/v1",
                  json={"token": user_2['token'], "channel_id": channel['channel_id']})

    # Attempt to view messages from a channel which the user is no longer a member of
    start = 0
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user_2['token'], "channel_id": channel['channel_id'], "start": start})
    assert response.status_code == AccessError.code

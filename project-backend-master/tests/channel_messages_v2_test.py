'''
This test fle aims to validate the functionality of the channel/messages/v2
http route using pytest.

Functions:
    clear_register_user_and_create_channel()
    test_valid_input()
    test_invalid_channel_id()
    test_start_not_0_for_empty_channel()
    test_start_greater_than_message_total()
    test_user_not_member_of_channel()
    test_correct_return_type()
    test_pagination
    test_end_neg1_less_than_50_msgs()
    test_end_neg1_for_between_50_and_100_msgs()
    test_end_neg1_for_between_100_and_150_msgs()
'''
import pytest
import requests
from src.error import InputError, AccessError
from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_user_and_create_channel():
    '''
    This function is a fixture used to clear the system, register
    a new user, login this new user and create a new channel which
    this user is a member of.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password",
                                   "name_first": "John", "name_last": "Smith"})

    user = response.json()

    response = requests.post(f"{BASE_URL}/channels/create/v2",
                             json={"token": user['token'], "name": "Badger Channel", "is_public": True})
    channel = response.json()
    return user, channel


def test_valid_input(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns a status code of 200 with valid input.
    '''
    user, channel = clear_register_user_and_create_channel
    start = 0

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['messages'] == []
    assert response_data['start'] == 0
    assert response_data['end'] == -1


def test_invalid_channel_id(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns an InputError when the user
    attemps to view messages from a channel which doesn't exist.
    '''
    user = clear_register_user_and_create_channel[0]
    channel_id = 5
    start = 0

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel_id, "start": start})
    assert response.status_code == InputError.code


def test_start_not_0_for_empty_channel(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns an InputError when start is set to a value
    greater than 0 for a channel with no messages.
    '''
    user, channel = clear_register_user_and_create_channel
    start = 1

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    assert response.status_code == InputError.code


def test_start_greater_than_message_total(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns an InputError when start is set to a value
    greater than the total number of messages in the channel.
    '''
    user, channel = clear_register_user_and_create_channel
    start = 3

    for _ in range(0, 3):
        requests.post(f"{BASE_URL}/message/send/v1",
                      json={"token": user["token"], "channel_id": channel["channel_id"],
                            "message": "Hello"})

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    assert response.status_code == InputError.code


def test_user_not_member_of_channel(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns an AccessError when the channel_id
    is valid, but the user is not a member of the channel user.
    '''
    channel = clear_register_user_and_create_channel[1]
    start = 0
    token = 5

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": token, "channel_id": channel['channel_id'], "start": start})
    assert response.status_code == AccessError.code


def test_correct_return_type(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns the correct variable types.
    '''
    user, channel = clear_register_user_and_create_channel
    start = 0

    requests.post(f"{BASE_URL}/message/send/v1",
                  json={"token": user["token"], "channel_id": channel["channel_id"],
                        "message": "Hello"})

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})

    response_data = response.json()
    message_0 = response_data['messages'][0]
    assert isinstance(response_data['messages'], list) is True
    assert isinstance(response_data['start'], int) is True
    assert isinstance(response_data['end'], int) is True
    assert isinstance(message_0['message_id'], int) is True
    assert isinstance(message_0['u_id'], int) is True
    assert isinstance(message_0['message'], str) is True
    assert isinstance(message_0['time_sent'], int) is True
    assert isinstance(message_0['reacts'], list) is True
    assert isinstance(message_0['is_pinned'], bool) is True


def test_pagination(clear_register_user_and_create_channel):
    '''
    Verifies the function produces pagination correctly.
    Test will send 123 messages.
    Channel messages will be called for start 0.
    The message with index = 0 should be the 73rd message sent.
    The message with index = 49 should be the 24th message sent.
    Return value for 'end' should be 50

    Channel messages will be called for start 50.
    The message with index = 0 should be the 23rd message sent.
    The message with index = 49 should be the 1st message sent.
    Return value for 'end' should be -1
    '''
    user, channel = clear_register_user_and_create_channel

    for send in range(0, 73):
        requests.post(f"{BASE_URL}/message/send/v1",
                      json={"token": user["token"], "channel_id": channel["channel_id"],
                            "message": f"message {send + 1}"})

    start = 0
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    response_data = response.json()

    most_recent_message = response_data['messages'][0]
    assert most_recent_message['message'] == "message 73"

    least_recent_message = response_data['messages'][49]
    assert least_recent_message['message'] == "message 24"

    assert response_data["end"] == 50

    start = 50
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    response_data = response.json()

    most_recent_message = response_data['messages'][0]
    assert most_recent_message['message'] == "message 23"

    least_recent_message = response_data['messages'][22]
    assert least_recent_message['message'] == "message 1"

    assert response_data["end"] == -1


def test_end_neg1_less_than_50_msgs(clear_register_user_and_create_channel):
    '''
    Verifies that channel/messages/v2 returns end = -1 for a channel with less than 50 messages.
    '''
    user, channel = clear_register_user_and_create_channel
    start = 0

    for send in range(0, 2):
        requests.post(f"{BASE_URL}/message/send/v1",
                      json={"token": user["token"], "channel_id": channel["channel_id"],
                            "message": f"message {send + 1}"})

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    response_data = response.json()

    most_recent_message = response_data['messages'][0]
    assert most_recent_message['message'] == "message 2"

    least_recent_message = response_data['messages'][1]
    assert least_recent_message['message'] == "message 1"

    assert response_data["end"] == -1


def test_is_this_user_reacted(clear_register_user_and_create_channel):
    '''
    This test verifies that is_this_user_reacted for each
    message correctly reflects whether or not the user calling
    channel/messages has reacted.
    '''
    user_1, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "adam.smith@unsw.edu.au", "password": "password",
                                   "name_first": "Adam", "name_last": "Smith"})
    user_2 = response.json()

    requests.post(f"{BASE_URL}/channel/join/v2",
                  json={"token": user_2["token"], "channel_id": channel["channel_id"]})

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_1["token"], "channel_id": channel["channel_id"],
                                   "message": "message"})
    message0_id = response.json()

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_1["token"], "channel_id": channel["channel_id"],
                                   "message": "message"})
    message1_id = response.json()

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_2["token"], "channel_id": channel["channel_id"],
                                   "message": "message"})
    message2_id = response.json()

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_2["token"], "channel_id": channel["channel_id"],
                                   "message": "message"})
    message3_id = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={'token': user_1['token'], 'message_id': message0_id['message_id'],
                        'react_id': react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={'token': user_2['token'], 'message_id': message1_id['message_id'],
                        'react_id': react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={'token': user_1['token'], 'message_id': message2_id['message_id'],
                        'react_id': react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={'token': user_2['token'], 'message_id': message3_id['message_id'],
                        'react_id': react_id})

    start = 0
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": user_1['token'], "channel_id": channel['channel_id'],
                                    "start": start})
    response_data = response.json()
    message_0 = response_data['messages'][3]['reacts'][0]
    message_1 = response_data['messages'][2]['reacts'][0]
    message_2 = response_data['messages'][1]['reacts'][0]
    message_3 = response_data['messages'][0]['reacts'][0]

    assert message_0['is_this_user_reacted'] == True
    assert message_1['is_this_user_reacted'] == False
    assert message_2['is_this_user_reacted'] == True
    assert message_3['is_this_user_reacted'] == False

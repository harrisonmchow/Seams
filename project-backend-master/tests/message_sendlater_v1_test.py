'''
This test file aims to validate the functionaility of message/send/v1 and the front end. 

Functions:
    clear
    register_and_login1
    register_and_login2
    create_channel

    test_invalid_message_too_short
    test_invalid_message_too_long
    test_invalid_id
    test_invalid_token
    test_invalid_channel
    test_user_not_in_channel
    test_invalid_time
    test_valid_message_sendlater

    test_edit_msg_before_sent
    test_delete_msg_before_sent
    test_remove_msg_before_sent

'''

import pytest
import requests
from src.error import InputError, AccessError
from datetime import datetime
import time
from src.config import url
from src.other import encode_token
BASE_URL = url


@pytest.fixture
def clear():
    print(f"Clearing. Running: {BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200


@pytest.fixture
def register_and_login1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    id = data['auth_user_id']
    return token, id


@pytest.fixture
def register_and_login2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                   "password": "passworD1234655", "name_first": "James", "name_last": "Bob"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    id = data['auth_user_id']
    return token, id


def create_channel(token, name, is_public):
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": is_public})
    assert response_input.status_code == 200

    channel_id = response_input.json()
    return channel_id


# --------------------------------------------------------------------------------------------------


def test_invalid_message_too_short(clear, register_and_login1):
    '''
    try to send an invalid message
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", True)
    time = datetime.timestamp(datetime.now()) + 100
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": "", "time_sent": time})
    assert response_input.status_code == InputError.code


def test_invalid_message_too_long(clear, register_and_login1):
    '''
    try to send an invalid message
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", True)
    message = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula\
    eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes,\
    nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis\
    , sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec\
    , vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,\
    justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus\
    elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu,\
    consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a,\
    tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet.\
    Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam \
    rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet \
    adipiscing sem neque sed ipsum. Nam quam nu"
    assert len(message) > 1000
    time = datetime.timestamp(datetime.now()) + 100

    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": message, "time_sent": time})
    assert response_input.status_code == InputError.code


def test_invalid_id(clear, register_and_login1):
    '''
    invalid user id tries to send a message
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    channel = create_channel(token1, "Channel 1", True)
    time = datetime.timestamp(datetime.now()) + 100
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": invalid_token,
                                                                             "channel_id": channel['channel_id'], "message": "Hi my name Jeff", "time_sent": time})
    assert response_input.status_code == AccessError.code


def test_invalid_token(clear, register_and_login1):
    '''
    invalid token format tries to send a message
    '''
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    time = datetime.timestamp(datetime.now()) + 100
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": -1,
                                                                             "channel_id": channel['channel_id'], "message": "Hi my name Jeff", "time_sent": time})
    assert response_input.status_code == AccessError.code


def test_invalid_channel(clear, register_and_login1):
    '''
    valid user tries to send a message to invalid channel id
    '''
    token = register_and_login1[0]
    invalid_ch_id = 5
    message = "Hi my name Jeff"
    time = datetime.timestamp(datetime.now()) + 100
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": invalid_ch_id, "message": message, "time_sent": time})
    assert response_input.status_code == InputError.code


def test_user_not_in_channel(clear, register_and_login1, register_and_login2):
    '''
    valid user tries to send a message to a channel they are not in
    '''
    token1 = register_and_login1[0]
    token2 = register_and_login2[0]
    channel = create_channel(token1, "Channel 1", True)
    time = datetime.timestamp(datetime.now()) + 100
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token2,
                                                                             "channel_id": channel['channel_id'], "message": "Hi my name Jeff", "time_sent": time})
    assert response_input.status_code == AccessError.code


def test_invalid_time(clear, register_and_login1):
    '''
    try to send a message in the past
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", True)
    time = datetime.timestamp(datetime.now()) - 2000
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": "1", "time_sent": time})
    assert response_input.status_code == InputError.code


def test_valid_message_sendlater(clear, register_and_login1):
    '''
    send a message 1 second in the future
    '''
    token = register_and_login1[0]
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                   "password": "passworD1234655", "name_first": "James", "name_last": "Bob"})
    assert response.status_code == 200
    create_channel(token, "Channel 0", True)
    channel = create_channel(token, "Channel 1", True)
    time_sent = int(datetime.timestamp(datetime.now())) + 1
    message = "Hi, I am from the future @jamesbob"
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": message, "time_sent": time_sent})
    assert response_input.status_code == 200

    # check there are no messages sent in the channel
    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": token, "channel_id": channel['channel_id'],
                                    "start": 0})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data['messages']) == 0

    #  wait 1.5 seconds before checking if the message sent correctly
    time.sleep(1.5)

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": token, "channel_id": channel['channel_id'],
                                    "start": 0})
    assert response.status_code == 200
    response_data = response.json()
    most_recent_msg = response_data['messages'][0]
    assert most_recent_msg['message'] == message

# --------------------------------------------------------------------------------------------------
# Testing if it works with other functions.


def test_edit_msg_before_sent(clear, register_and_login1):
    '''
    send a message 100 seconds in the future and try to edit it before it sends
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", True)
    time_sent = datetime.timestamp(datetime.now()) + 100
    message = "Hi, I am from the future"
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": message, "time_sent": time_sent})
    assert response_input.status_code == 200
    message_id = response_input.json()['message_id']
    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                       "message_id": message_id, "message": "new message"})
    assert response_input.status_code == InputError.code


def test_delete_msg_before_sent(clear, register_and_login1):
    '''
    send a message 100 seconds in the future and try to edit it before it sends
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", True)
    time_sent = datetime.timestamp(datetime.now()) + 100
    message = "Hi, I am from the future"
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": message, "time_sent": time_sent})
    assert response_input.status_code == 200
    message_id = response_input.json()['message_id']
    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                       "message_id": message_id, "message": ""})
    assert response_input.status_code == InputError.code


def test_remove_msg_before_sent(clear, register_and_login1):
    '''
    send a message 100 seconds in the future and try to edit it before it sends
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", True)
    time_sent = datetime.timestamp(datetime.now()) + 100
    message = "Hi, I am from the future"
    response_input = requests.post(f"{BASE_URL}/message/sendlater/v1", json={"token": token,
                                                                             "channel_id": channel['channel_id'], "message": message, "time_sent": time_sent})
    assert response_input.status_code == 200
    message_id = response_input.json()['message_id']

    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token,
                                                                      'message_id': message_id})
    assert response.status_code == InputError.code

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
    test_valid_channel
    test_multiple_messages
'''

import pytest
import requests
from src.error import InputError, AccessError
from datetime import datetime
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
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": ""})
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

    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == InputError.code


def test_invalid_id(clear, register_and_login1):
    '''
    invalid user id tries to send a message
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": invalid_token,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_invalid_token(clear, register_and_login1):
    '''
    invalid token format tries to send a message
    '''
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": -1,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_invalid_channel(clear, register_and_login1):
    '''
    valid user tries to send a message to invalid channel id
    '''
    token = register_and_login1[0]
    invalid_ch_id = 5
    message = "Hi my name Jeff"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": invalid_ch_id, "message": message})
    assert response_input.status_code == InputError.code


def test_user_not_in_channel(clear, register_and_login1, register_and_login2):
    '''
    valid user tries to send a message to a channel they are not in
    '''
    token1 = register_and_login1[0]
    token2 = register_and_login2[0]
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token2,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_valid_channel(clear, register_and_login1, register_and_login2):
    '''
    valid user send a message to a channel
    '''
    token, auth_id = register_and_login1
    create_channel(token, "Channel 1", False)
    channel = create_channel(token, "Channel 2", False)

    message = "Hi my name Jeffn @jamesbob"
    time_sent_lower = int(datetime.timestamp(datetime.now()))
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    assert data['message_id'] == 1

    expected_message_id = 1
    expected_u_id = auth_id
    expected_message = message
    time_sent_upper = time_sent_lower + 1

    response2 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token,
                                                                        "channel_id": channel['channel_id'], "start": 0})

    assert response2.status_code == 200
    data = response2.json()
    assert data['messages'][0]['message_id'] == expected_message_id
    assert data['messages'][0]['u_id'] == expected_u_id
    assert data['messages'][0]['message'] == expected_message
    assert time_sent_lower <= data['messages'][0]['time_sent'] <= time_sent_upper


def test_multiple_messages(clear, register_and_login1):
    '''
    valid user sends multiple messages to a channel
    '''
    token, auth_id = register_and_login1
    channel = create_channel(token, "Channel 1", False)

    # send a message
    message1 = "Hi my name is jeff"
    time_sent1_lower = int(datetime.timestamp(datetime.now()))
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message1})
    assert response_input.status_code == 200
    data = response_input.json()
    assert data['message_id'] == 1

    # send another message
    message2 = "Damn this project kinda hard"
    time_sent2_lower = int(datetime.timestamp(datetime.now()))
    response_input2 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                         "channel_id": channel['channel_id'], "message": message2})
    assert response_input2.status_code == 200
    data2 = response_input2.json()
    assert data2['message_id'] == 2

    expected_message_id1 = 1
    expected_u_id1 = auth_id
    expected_message1 = message1
    time_sent1_upper = time_sent1_lower + 1

    expected_message_id2 = 2
    expected_u_id2 = auth_id
    expected_message2 = message2
    time_sent2_upper = time_sent2_lower + 1

    response3 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token,
                                                                        "channel_id": channel['channel_id'], "start": 0})

    assert response3.status_code == 200

    returned = response3.json()
    assert returned['messages'][0]['message_id'] == expected_message_id2
    assert returned['messages'][0]['u_id'] == expected_u_id2
    assert returned['messages'][0]['message'] == expected_message2
    assert time_sent2_lower <= returned['messages'][0]['time_sent'] <= time_sent2_upper

    assert returned['messages'][1]['message_id'] == expected_message_id1
    assert returned['messages'][1]['u_id'] == expected_u_id1
    assert returned['messages'][1]['message'] == expected_message1
    assert time_sent1_lower <= returned['messages'][0]['time_sent'] <= time_sent1_upper

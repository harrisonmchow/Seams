'''
This test file aims to validate the functionaility of message/remove/v1 and the front end. 

Functions:
    clear
    register_and_login1
    register_and_login2
    create_channel

    test_invalid_msg_id_doesnt_exist
    test_user_trying_to_remove_others_msg_not_owner
    test_remove_own_message
    test_owner_removing_msg

    test_invalid_msg_id_doesnt_exist_dm
    test_non_owner_trying_to_remove_others_msg_dm
    test_remove_own_message_dm
    test_owner_removing_msg_dm
'''

import pytest
import requests
from src.other import encode_token
from src.error import InputError, AccessError
from datetime import datetime
from src.config import url
BASE_URL = url


@pytest.fixture
def clear():

    print(f"Clearing. Running: {BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200


@pytest.fixture
def register_and_login1():
    '''
    register and log in user
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    id = data['auth_user_id']
    return token, id


@pytest.fixture
def register_and_login2():
    '''
    register and log in user
    '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                   "password": "passworD1234655", "name_first": "James", "name_last": "Bob"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    id = data['auth_user_id']
    return token, id


def create_channel(token, name, is_public):
    '''
    create a channel
    '''
    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": name, "is_public": is_public})
    assert response_input.status_code == 200

    channel_id = response_input.json()
    return channel_id


def create_dm(token, u_ids):
    '''
    create a dm
    '''
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token,
                                                               "u_ids": u_ids})
    assert response.status_code == 200
    dm_id = response.json()['dm_id']
    return dm_id

# tests involving channels--------------------------------------------------------------------------


def test_invalid_id(clear, register_and_login1):
    '''
    user with invalid id tries to remove a message
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": invalid_token,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_invalid_token(clear, register_and_login1):
    '''
    user with invalid token format tries to remove a message
    '''
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": -1,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_invalid_msg_id_doesnt_exist(clear, register_and_login1):
    '''
    valid user tries to remove a message with an invalid message id
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", False)
    message = "Hi my name Jeff"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200

    response2 = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token,
                                                                       'message_id': 5})

    assert response2.status_code == InputError.code


def test_user_trying_to_remove_others_msg_not_owner(clear, register_and_login1, register_and_login2):
    '''
    user with invalid permissions tries to remove someone else's message
    '''
    # user 1 creates a channel then sends a message to it
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    message = "Hi my name Jeff"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token1,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    message_id = data['message_id']

    # user 2 joins the channel then tries to delete the message
    token2 = register_and_login2[0]
    join = requests.post(f"{BASE_URL}/channel/join/v2",
                         json={"token": token2, "channel_id": channel['channel_id']})
    assert join.status_code == 200
    response2 = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token2,
                                                                       'message_id': message_id})

    assert response2.status_code == AccessError.code


def test_remove_own_message(clear, register_and_login1):
    '''
    valid user removes their own message
    '''
    # user 1 creates a channel then sends a message to it
    token, auth_id = register_and_login1
    create_channel(token, "Channel 1", True)
    channel = create_channel(token, "Channel 2", False)
    message = "Hi my name Jeff"
    time_sent_lower = int(datetime.timestamp(datetime.now()))
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    message_id = data['message_id']

    # confirm that the message was created
    expected_message_id = message_id
    expected_u_id = auth_id
    expected_message = message
    time_sent_upper = time_sent_lower + 1

    response_input1 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token,
                                                                              "channel_id": channel['channel_id'], "start": 0})
    assert response_input1.status_code == 200
    result1 = response_input1.json()
    assert result1['messages'][0]['message_id'] == expected_message_id
    assert result1['messages'][0]['u_id'] == expected_u_id
    assert result1['messages'][0]['message'] == expected_message
    assert time_sent_lower <= result1['messages'][0]['time_sent'] <= time_sent_upper

    # user 1 then removes his own message. confirm it was actually removed
    response2 = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token,
                                                                       'message_id': message_id})
    assert response2.status_code == 200

    response_input2 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token,
                                                                              "channel_id": channel['channel_id'], "start": 0})
    assert response_input2.status_code == 200
    result2 = response_input2.json()
    assert len(result2['messages']) == 0


def test_owner_removing_msg(clear, register_and_login1, register_and_login2):
    '''
    user with owner permissions removes a message
    '''
    # user 1 creates a channel, which is then joined by user 2
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    token2, auth_id2 = register_and_login2

    response_join_channel = requests.post(f"{BASE_URL}/channel/join/v2", json={"token": token2,
                                                                               "channel_id": channel['channel_id']})

    assert response_join_channel.status_code == 200

    # get the second user to send a message
    message = "Hi my name Jeff"
    time_sent_lower = int(datetime.timestamp(datetime.now()))
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token2,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200
    message_id = response_input.json()["message_id"]

    # check the message was sent correctly
    expected_message_id = message_id
    expected_u_id = auth_id2
    expected_message = message
    time_sent_upper = time_sent_lower + 1

    response_input1 = requests.get(f"{BASE_URL}/channel/messages/v2",
                                   params={"token": token2, "channel_id": channel['channel_id'], "start": 0})
    assert response_input1.status_code == 200
    result1 = response_input1.json()
    assert result1['messages'][0]['message_id'] == expected_message_id
    assert result1['messages'][0]['u_id'] == expected_u_id
    assert result1['messages'][0]['message'] == expected_message
    assert time_sent_lower <= result1['messages'][0]['time_sent'] <= time_sent_upper

    # the owner (the first user) deletes the message
    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token1,
                                                                      'message_id': message_id})
    assert response.status_code == 200

    # check it was actually deleted
    response_input2 = requests.get(f"{BASE_URL}/channel/messages/v2",
                                   params={"token": token2, "channel_id": channel['channel_id'], "start": 0})
    assert response_input2.status_code == 200
    result2 = response_input2.json()
    assert len(result2['messages']) == 0

# tests involving dm--------------------------------------------------------------------------------


def test_invalid_msg_id_doesnt_exist_dm(clear, register_and_login1):
    '''
    message id doesn't exist
    '''
    token = register_and_login1[0]
    dm_id = create_dm(token, [])
    message = "Hi my name Jeff"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200

    # try delete some message that is invalid
    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token,
                                                                      'message_id': -1})

    assert response.status_code == InputError.code


def test_non_owner_trying_to_remove_others_msg_dm(clear, register_and_login1, register_and_login2):
    '''
    user in dm without owner permission tries to remove dm
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    dm_id = create_dm(token1, [id2])
    message = "Hi my name Jeff"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    # user 2 shouldn't be able to delete user 1's message, as hes not an owner.
    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token2,
                                                                      'message_id': message_id})
    assert response.status_code == AccessError.code


def test_remove_own_message_dm(clear, register_and_login1):
    '''
    user in dm removes their own dm
    '''
    token = register_and_login1[0]
    dm_id = create_dm(token, [])
    message = "Hi my name Jeff"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    # user 1 then wants to delete his own message
    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token,
                                                                      'message_id': message_id})
    assert response.status_code == 200
    # use dm/messages to find out if it was actually deleted later.


def test_owner_removing_msg_dm(clear, register_and_login1, register_and_login2):
    '''
    user in dm with owner permissions removes message
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    create_dm(token2, [])
    dm_id = create_dm(token1, [id2])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    # since user 1 is an owner of the dm, he can delete other peoples' messages
    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token1,
                                                                      'message_id': message_id})
    assert response.status_code == 200
    # use dm/messages to find out if it was actually deleted later.


def test_invalid_id_dm(clear, register_and_login1):
    '''
    invalid user id tries to remove message in dm
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    dm_id = create_dm(token1, [])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': message})
    data = response.json()
    message_id = data['message_id']

    response2 = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': invalid_token,
                                                                       'message_id': message_id})
    assert response2.status_code == AccessError.code


def test_invalid_token_dm(clear, register_and_login1):
    '''
    invalid user token format tries to remove message in dm
    '''
    token1 = register_and_login1[0]
    dm_id = create_dm(token1, [])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': message})
    data = response.json()
    message_id = data['message_id']

    response2 = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': -1,
                                                                       'message_id': message_id})
    assert response2.status_code == AccessError.code

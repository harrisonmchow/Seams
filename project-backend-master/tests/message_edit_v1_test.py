'''
This test file aims to validate the functionaility of message/edit/v1 and the front end. 

Functions:
    clear
    register_and_login1
    register_and_login2
    create_channel

    test_invalid_message_too_long
    test_invalid_message_id
    test_not_original_creator_making_change
    test_owner_permissions_making_changes
    test_empty_message
    test_change_own_message

    test_invalid_msg_id_dm
    test_message_too_long_dm
    test_not_original_creator_dm
    test_empty_message_dm
    test_edit_message_in_dm_owner
    test_edit_own_message_dm
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
    '''
    clear datastore
    '''
    print(f"Clearing. Running: {BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200


@pytest.fixture
def register_and_login1():
    '''
    register and log in a user
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
    register and log in a user
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
    an invalid user id tries to edit a message
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": invalid_token,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_invalid_token(clear, register_and_login1):
    '''
    an invalid token format tries to edit a message
    '''
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": -1,
                                                                        "channel_id": channel['channel_id'], "message": "Hi my name Jeff"})
    assert response_input.status_code == AccessError.code


def test_invalid_message_too_long(clear, register_and_login1):
    '''
    a valid user tries to edit a message but the new message is too long
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", False)
    message = "Hi my name Jeff"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    message_id = data['message_id']

    new_message = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula\
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
    assert len(new_message) > 1000

    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                       "message_id": message_id, "message": new_message})
    assert response_input.status_code == InputError.code


def test_invalid_message_id(clear, register_and_login1):
    '''
    a valid user tries to edit a message but the message_id is invalid
    '''
    token = register_and_login1[0]
    channel = create_channel(token, "Channel 1", False)
    message = "Hi my name Jeff"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel['channel_id'], "message": message})
    assert response_input.status_code == 200
    new_message = "some message"

    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                       "message_id": -1, "message": new_message})
    assert response_input.status_code == InputError.code


def test_not_original_creator_making_change(clear, register_and_login1, register_and_login2):
    '''
    a valid user who doesn't have permissions tries to edit someone else's message
    '''
    # register a user, then post a message to the channel
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", True)
    message = "Hi my name Jeff"
    response_input1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token1,
                                                                         "channel_id": channel['channel_id'], "message": message})
    assert response_input1.status_code == 200
    data = response_input1.json()
    message_id = data['message_id']

    # register user, join the channel, and then try edit the message
    token2 = register_and_login2[0]
    join = requests.post(f"{BASE_URL}/channel/join/v2",
                         json={"token": token2, "channel_id": channel['channel_id']})
    assert join.status_code == 200

    new_message = "some message"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token2,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == AccessError.code


def test_owner_permissions_making_changes(clear, register_and_login1, register_and_login2):
    '''
    testing an owner can edit someone else's message
    '''
    # register a user, then create a channel
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    channel = create_channel(token1, "Channel 1", True)
    message = "Hi my name Jeff"
    time_sent_lower = int(datetime.timestamp(datetime.now()))

    # another user joins the channel and sends a message
    join = requests.post(f"{BASE_URL}/channel/join/v2",
                         json={"token": token2, "channel_id": channel['channel_id']})
    assert join.status_code == 200
    response_input1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token2,
                                                                         "channel_id": channel['channel_id'], "message": message})
    assert response_input1.status_code == 200
    message_id = response_input1.json()['message_id']

    # since the first user is an owner, they can edit the message
    new_message = "some message"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200

    expected_message_id = message_id
    expected_u_id = id2
    expected_message = new_message
    time_sent_upper = time_sent_lower + 1

    response_input3 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token1,
                                                                              "channel_id": channel['channel_id'], "start": 0})

    assert response_input3.status_code == 200
    data = response_input3.json()
    assert data['messages'][0]['message_id'] == expected_message_id
    assert data['messages'][0]['u_id'] == expected_u_id
    assert data['messages'][0]['message'] == expected_message
    assert time_sent_lower <= data['messages'][0]['time_sent'] <= time_sent_upper


def test_empty_message(clear, register_and_login1):
    '''
    a valid user edits a message to be empty, so the message is deleted.
    '''
    token1 = register_and_login1[0]
    channel = create_channel(token1, "Channel 1", False)
    message = "Hi my name Jeff"
    response_input1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token1,
                                                                         "channel_id": channel['channel_id'], "message": message})
    assert response_input1.status_code == 200
    message_id = response_input1.json()["message_id"]
    new_message = ""

    # since the new message is empty, it should delete the message
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200

    response_input3 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token1,
                                                                              "channel_id": channel['channel_id'], "start": 0})

    data = response_input3.json()
    assert data['messages'] == []


def test_change_own_message(clear, register_and_login1):
    '''
    a valid user edits their own message
    '''
    token1, id1 = register_and_login1
    channel = create_channel(token1, "Channel 1", False)
    message = "Hi my name Jeff"
    time_sent_lower = int(datetime.timestamp(datetime.now()))
    response_input1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token1,
                                                                         "channel_id": channel['channel_id'], "message": message})
    assert response_input1.status_code == 200
    message_id = response_input1.json()["message_id"]

    # change the original message
    new_message = "My name actually Geoff"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200

    response_input3 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token1,
                                                                              "channel_id": channel['channel_id'], "start": 0})

    expected_message_id = message_id
    expected_u_id = id1
    expected_message = new_message
    time_sent_upper = time_sent_lower + 1

    data = response_input3.json()
    assert data['messages'][0]['message_id'] == expected_message_id
    assert data['messages'][0]['u_id'] == expected_u_id
    assert data['messages'][0]['message'] == expected_message
    assert time_sent_lower <= data['messages'][0]['time_sent'] <= time_sent_upper


def test_change_own_message2(clear, register_and_login1, register_and_login2):
    '''
    a valid user edits their own message
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    create_channel(token1, "Channel 1", True)
    channel = create_channel(token1, "Channel 2", True)
    message1 = "Hi my name Jeff"

    # another user joins the channel and sends a message
    join = requests.post(f"{BASE_URL}/channel/join/v2",
                         json={"token": token2, "channel_id": channel['channel_id']})
    assert join.status_code == 200
    response_input1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token2,
                                                                         "channel_id": channel['channel_id'], "message": message1})
    assert response_input1.status_code == 200

    # send another message, which will be editted
    message2 = "But my name isn't spelt with a J"
    time_sent_lower = int(datetime.timestamp(datetime.now()))
    response_input2 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token2,
                                                                         "channel_id": channel['channel_id'], "message": message2})
    assert response_input2.status_code == 200
    message_id = response_input2.json()['message_id']

    # since the second user is the original creator of the message, he can edit it.
    new_message = "some message @jamesbob"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token2,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200

    expected_message_id = message_id
    expected_u_id = id2
    expected_message = new_message
    time_sent_upper = time_sent_lower + 1

    response_input3 = requests.get(f"{BASE_URL}/channel/messages/v2", params={"token": token1,
                                                                              "channel_id": channel['channel_id'], "start": 0})

    assert response_input3.status_code == 200
    data = response_input3.json()
    assert data['messages'][0]['message_id'] == expected_message_id
    assert data['messages'][0]['u_id'] == expected_u_id
    assert data['messages'][0]['message'] == expected_message
    assert time_sent_lower <= data['messages'][0]['time_sent'] <= time_sent_upper

# tests involving dm--------------------------------------------------------------------------------


def test_invalid_msg_id_dm(clear, register_and_login1, register_and_login2):
    '''
    trying to edit an invalid message id
    '''
    # create a dm between 2 users, then send a message
    token = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token, [id2])
    message = "Hi my name Jeff"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200

    # attempt to edit another message with an invalid id
    new_message = "some message"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                        "message_id": -1, "message": new_message})
    assert response_input2.status_code == InputError.code


def test_message_too_long_dm(clear, register_and_login1):
    '''
    trying to edit a message with a message too long
    '''
    token = register_and_login1[0]
    dm_id = create_dm(token, [])
    message = "Hi my name Jeff"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    new_message = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula\
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
    assert len(new_message) > 1000

    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                       "message_id": message_id, "message": new_message})
    assert response_input.status_code == InputError.code


def test_not_original_creator_dm(clear, register_and_login1, register_and_login2):
    '''
    a valid user without owner permissions tries to edit someone else's message
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

    # user 2 shouldn't be able to edit user 1's message, as hes not an owner.
    new_message = "some message"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token2,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == AccessError.code


def test_empty_message_dm(clear, register_and_login1, register_and_login2):
    '''
    a valid user edits a message to be empty, so it is deleted
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    dm_id = create_dm(token1, [id2])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    # since the new message is empty, the message should be deleted.
    new_message = ""
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200
    # wait for dm/messages to see if it was actually deleted.


def test_edit_message_in_dm_owner(clear, register_and_login1, register_and_login2):
    '''
    a user with owner permissions edits a message in a dm
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    dm_id = create_dm(token1, [id2])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    # since the first user is an owner of the dm, he can edit the message
    new_message = "some message"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200
    # gotta wait for dm_messages to see if the message actually changed


def test_edit_own_message_dm(clear, register_and_login1, register_and_login2):
    '''
    a valid user edits their own message in a dm
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    create_dm(token2, [])
    dm_id = create_dm(token1, [id2])
    message1 = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                                    'dm_id': dm_id, 'message': message1})
    assert response.status_code == 200

    message2 = "my name is Jeff"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                                    'dm_id': dm_id, 'message': message2})
    assert response.status_code == 200
    data = response.json()
    message_id = data['message_id']

    # since he is editting his own message, it should be changed
    new_message = "Goodbye, you smell"
    response_input2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token2,
                                                                        "message_id": message_id, "message": new_message})
    assert response_input2.status_code == 200
    # check if it changed using dms/messages


def test_invalid_id_dm(clear, register_and_login1):
    '''
    user with in invalid id tries to edit a message
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    dm_id = create_dm(token1, [])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': message})
    data = response.json()
    message_id = data['message_id']

    new_message = "Goodbye, you smell"
    response2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": invalid_token,
                                                                  "message_id": message_id, "message": new_message})
    assert response2.status_code == AccessError.code


def test_invalid_token_dm(clear, register_and_login1):
    '''
    an invalid token format tries to edit a message
    '''
    token1 = register_and_login1[0]
    dm_id = create_dm(token1, [])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': message})
    data = response.json()
    message_id = data['message_id']

    new_message = "Goodbye, you smell"
    response2 = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": -1,
                                                                  "message_id": message_id, "message": new_message})
    assert response2.status_code == AccessError.code

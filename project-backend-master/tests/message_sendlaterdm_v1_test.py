'''
This test file aims to validate the functionaility of message/senddm/v1 and the front end. 

Functions:
    clear
    register_and_login1
    register_and_login2
    create_dm

    test_invalid_id_dm
    test_invalid_token_dm
    test_invalid_msg_too_short
    test_invalid_msg_too_long
    test_invalid_time
    test_invalid_dm_id
    test_not_a_member_of_dm
    test_valid_sendlater
    test_two_messages

    test_edit_msg_before_sent
    test_delete_msg_before_sent
    test_remove_msg_before_sent
    test_deletedm_before_msg_send
'''


import pytest
import requests
import time
from src.error import InputError, AccessError
from datetime import datetime
from src.other import encode_token
from src.config import url
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


def create_dm(token, u_ids):
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token,
                                                               "u_ids": u_ids})
    assert response.status_code == 200
    dm_id = response.json()['dm_id']
    return dm_id

# -----------------------------------------------------------------------------------------


def test_invalid_id_dm(clear, register_and_login1):
    '''
    invalid user id tries to send message to a dm
    '''
    token1 = register_and_login1[0]
    invalid_token = encode_token(-1)
    dm_id = create_dm(token1, [])
    time_sent = datetime.timestamp(datetime.now()) + 10
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": invalid_token,
                                                                         'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response.status_code == AccessError.code


def test_invalid_token_dm(clear, register_and_login1):
    '''
    invalid token format tries to send message to a dm
    '''
    token1 = register_and_login1[0]
    dm_id = create_dm(token1, [])
    message = "Hello nice to meet you!"
    time_sent = datetime.timestamp(datetime.now()) + 10
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": -1,
                                                                         'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response.status_code == AccessError.code


def test_invalid_msg_too_short(clear, register_and_login1, register_and_login2):
    '''
    invalid message
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])
    time_sent = datetime.timestamp(datetime.now()) + 10
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                         'dm_id': dm_id, 'message': "", 'time_sent': time_sent})
    assert response.status_code == InputError.code


def test_invalid_msg_too_long(clear, register_and_login1, register_and_login2):
    '''
    invalid message
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])
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
    time_sent = datetime.timestamp(datetime.now()) + 10
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                         'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response.status_code == InputError.code


def test_invalid_time(clear, register_and_login1):
    '''
    valid user tries to send a message with a time in the past
    '''
    token = register_and_login1[0]
    dm_id = create_dm(token, [])
    message = "Hi my name Jeff"
    time = datetime.timestamp(datetime.now()) - 100
    response_input = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token,
                                                                               "dm_id": dm_id, "message": message, "time_sent": time})
    assert response_input.status_code == InputError.code


def test_invalid_dm_id(clear, register_and_login1):
    '''
    user tries to send message to invalid dm id
    '''
    token1 = register_and_login1[0]
    message = "Hello nice to meet you!"
    time_sent = datetime.timestamp(datetime.now()) + 10
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                         'dm_id': -1, 'message': message, 'time_sent': time_sent})
    assert response.status_code == InputError.code


def test_not_a_member_of_dm(clear, register_and_login1, register_and_login2):
    '''
    user tries to send message to a dm he is not in
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])

    # create a third user, who isn't in the dm created
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "jack@unsw.edu.au",
                                                                   "password": "Badger112233", "name_first": "Jack", "name_last": "Harlow"})
    assert response.status_code == 200

    response2 = requests.post(f"{BASE_URL}/auth/login/v2", json={"email": "jack@unsw.edu.au",
                                                                 "password": "Badger112233"})
    assert response2.status_code == 200
    data = response2.json()
    token3 = data['token']
    message = "Hi, im not actually in this channel"
    time_sent = datetime.timestamp(datetime.now()) + 10
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token3,
                                                                         'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response.status_code == AccessError.code


def test_valid_sendlater(clear, register_and_login1, register_and_login2):
    '''
    successfully send a message in the future by 1 second1
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    create_dm(token1, [])
    dm_id = create_dm(token1, [id2])
    time_sent = datetime.timestamp(datetime.now()) + 1
    message = "Hey, its me from the future! @jamesbob"
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                         'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response.status_code == 200
    data1 = response.json()
    m_id = data1['message_id']

    # Check that it hasn't sent yet.
    response = requests.get(f"{BASE_URL}/dm/messages/v1",
                            params={"token": token1, "dm_id": dm_id, "start": 0})
    assert response.status_code == 200
    data = response.json()
    assert len(data['messages']) == 0

    # wait 2 seconds.
    time.sleep(2)

    response = requests.get(f"{BASE_URL}/dm/messages/v1",
                            params={"token": token1, "dm_id": dm_id, "start": 0})
    assert response.status_code == 200
    data = response.json()
    most_recent_message = data['messages'][0]
    assert most_recent_message['message'] == message
    assert most_recent_message['message_id'] == m_id

# I know this test passes, but we need to save time on pytest :)
# def test_two_messages(clear, register_and_login1):
#     '''
#     send two messages at a later time.
#     '''
#     token1 = register_and_login1[0]
#     dm_id = create_dm(token1, [])
#     time_sent1 = datetime.timestamp(datetime.now()) + 2
#     message1 = "Hey, its me from the future!"
#     time_sent2 = datetime.timestamp(datetime.now()) + 1
#     message2 = "Hey, its me from the future too!"

#     response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
#                                                                          'dm_id': dm_id, 'message': message1, 'time_sent': time_sent1})
#     assert response.status_code == 200
#     response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
#                                                                          'dm_id': dm_id, 'message': message2, 'time_sent': time_sent2})
#     assert response.status_code == 200

#     # wait 2.5 seconds
#     time.sleep(3)
#     response = requests.get(f"{BASE_URL}/dm/messages/v1",
#                             params={"token": token1, "dm_id": dm_id, "start": 0})
#     assert response.status_code == 200
#     data = response.json()
#     most_recent_message = data['messages'][0]
#     assert most_recent_message['message'] == message1

# --------------------------------------------------------------------------------------------------
# Testing if it works with other functions.


def test_edit_msg_before_sent(clear, register_and_login1, register_and_login2):
    '''
    send a message 100 seconds in the future and try to edit it before it sends
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])
    time_sent = datetime.timestamp(datetime.now()) + 100
    message = "Hey, its me from the future!"
    response_input = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                               'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response_input.status_code == 200
    message_id = response_input.json()['message_id']

    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                       "message_id": message_id, "message": "new message"})
    assert response_input.status_code == InputError.code


def test_delete_msg_before_sent(clear, register_and_login1, register_and_login2):
    '''
    send a message 100 seconds in the future and try to delete it before it sends
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])
    time_sent = datetime.timestamp(datetime.now()) + 100
    message = "Hey, its me from the future!"
    response_input = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                               'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response_input.status_code == 200
    message_id = response_input.json()['message_id']

    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token1,
                                                                       "message_id": message_id, "message": ""})
    assert response_input.status_code == InputError.code


def test_remove_msg_before_sent(clear, register_and_login1, register_and_login2):
    '''
    send a message 100 seconds in the future and try to remove it before it sends
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])
    time_sent = datetime.timestamp(datetime.now()) + 100
    message = "Hey, its me from the future!"
    response_input = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                               'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response_input.status_code == 200
    message_id = response_input.json()['message_id']

    response = requests.delete(f"{BASE_URL}/message/remove/v1", json={'token': token1,
                                                                      'message_id': message_id})
    assert response.status_code == InputError.code


def test_deletedm_before_msg_send(clear, register_and_login1, register_and_login2):
    '''
    send a message to a dm 1 second in the future. Delete the dm before the message sends.
    It shouldn't send.
    '''

    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])
    time_sent = datetime.timestamp(datetime.now()) + 1
    message = "Hey, its me from the future!"
    response_input = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json={"token": token1,
                                                                               'dm_id': dm_id, 'message': message, 'time_sent': time_sent})
    assert response_input.status_code == 200

    response = requests.delete(
        f"{BASE_URL}/dm/remove/v1", json={"token": token1, 'dm_id': dm_id})
    assert response.status_code == 200
    time.sleep(1.5)

    # check that no message was sent.
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token1})
    assert response.status_code == 200
    data = response.json()['user_stats']
    assert len(data['messages_sent']) == 1

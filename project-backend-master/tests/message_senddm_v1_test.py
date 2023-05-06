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
    test_invalid_dm_id
    test_not_a_member_of_dm
    test_successfully_message
'''


import pytest
import requests
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
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": invalid_token,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == AccessError.code


def test_invalid_token_dm(clear, register_and_login1):
    '''
    invalid token format tries to send message to a dm
    '''
    token1 = register_and_login1[0]
    dm_id = create_dm(token1, [])
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": -1,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == AccessError.code


def test_invalid_msg_too_short(clear, register_and_login1, register_and_login2):
    '''
    invalid message
    '''
    token1 = register_and_login1[0]
    id2 = register_and_login2[1]
    dm_id = create_dm(token1, [id2])

    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': ""})
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

    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == InputError.code


def test_invalid_dm_id(clear, register_and_login1):
    '''
    user tries to send message to invalid dm id
    '''
    token1 = register_and_login1[0]
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': -1, 'message': message})
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

    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token3,
                                                                    'dm_id': dm_id, 'message': message})
    assert response.status_code == AccessError.code


def test_successfully_message(clear, register_and_login1, register_and_login2):
    '''
    Successfully exchange messages in dms
    '''
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    # create 2 dms, and send messages to 1 of them
    create_dm(token1, [])
    dm_id = create_dm(token1, [id2])
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token1,
                                                                    'dm_id': dm_id, 'message': "Hi, its nice to meet you @jamesbob"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data['message_id'], int) == True

    response2 = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token2,
                                                                     'dm_id': dm_id, 'message': "Beans Beans Beans"})
    assert response2.status_code == 200
    data = response2.json()
    assert isinstance(data['message_id'], int) == True

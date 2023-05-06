'''
This test fle aims to validate the functionality of the message/unreact/v1
http route using pytest.

Functions:
    clear_register_user_and_create_channel()
    clear_register_users_and_create_dm()
    test_channel_message_check_return_type()
    test_dm_message_check_return_type()
    test_channel_message_id_invalid()
    test_dm_message_id_invalid()
    test_react_id_invalid()
    test_react_id_valid_then_invalid()
    test_no_react_channel()
    test_no_react_dm()
    test_not_member_of_channel()
    test_not_member_of_dm()
    test_two_users_react_unreact_channel()
    test_two_users_unreact_dm()
    test_two_consecutive_unreacts_channel()
    test_two_consecutive_unreacts_dm()
    test_unreact_someone_else_message_channel()
    test_unreact_someone_else_react_channel()
    test_unreact_someone_else_react_dm()
'''
import pytest
import requests
from src.error import InputError
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


@pytest.fixture
def clear_register_users_and_create_dm():
    '''
    This function is a fixture used to clear the system, register
    two new users and login both new users. User 1 creates
    a new dm which is directed to user 2.
    '''
    requests.delete(f"{BASE_URL}/clear/v1")
    requests.post(f"{BASE_URL}/auth/register/v2",
                  json={"email": "john.smith@unsw.edu.au", "password": "password",
                        "name_first": "John", "name_last": "Smith"})

    requests.post(f"{BASE_URL}/auth/register/v2",
                  json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD",
                        "name_first": "Will", "name_last": "Jones"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "john.smith@unsw.edu.au", "password": "password"})
    user_1 = response.json()
    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD"})
    user_2 = response.json()

    response = requests.post(f"{BASE_URL}/dm/create/v1",
                             json={"token": user_1['token'], "u_ids": [user_2['auth_user_id']]})
    dm = response.json()
    return user_1, user_2, dm


def test_channel_message_check_return_type(clear_register_user_and_create_channel):
    '''
    This test verifies that a user can unreact to a
    message in a channel and the HTTP route returns
    a status code of 200 and that the return is {}.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user["token"], "message_id": message_id["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={'token': user['token'], 'message_id': message_id['message_id'],
                                   'react_id': react_id})
    response_data = response.json()

    assert response.status_code == 200
    assert isinstance(response_data, dict) is True


def test_dm_message_check_return_type(clear_register_users_and_create_dm):
    '''
    This test verifies that a user can unreact to a
    message in a dam and the HTTP route returns a
    status code of 200 and that the return is {}.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/react/v1",
                             json={"token": user["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={'token': user['token'], 'message_id': message_id['message_id'],
                                   'react_id': react_id})
    response_data = response.json()

    assert response.status_code == 200
    assert isinstance(response_data, dict) is True


def test_channel_message_id_invalid(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to react
    to a message which has been sent to a channel with
    the incorrect message_id, an input error is raised.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": "Hello"})

    invalid_message_id = 2
    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": invalid_message_id, "react_id": react_id})
    assert response.status_code == InputError.code


def test_dm_message_id_invalid(clear_register_users_and_create_dm):
    '''
    This test verifies that if a user tries to react
    to a message which has been sent to a dm with
    the incorrect message_id, an input error is raised.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": f"Hello"})

    invalid_message_id = 2
    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": invalid_message_id, "react_id": react_id})
    assert response.status_code == InputError.code


def test_react_id_invalid(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to react
    with an invalid react_id, an input error is raised.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    react_id = 2
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == InputError.code


def test_react_id_valid_then_invalid(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to react
    with an invalid react_id, an input error is raised.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})

    react_id = 2
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == InputError.code


def test_no_react_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to unreact
    with a react_id which they have not used on
    a message in a channel, an input error is raised.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == InputError.code


def test_no_react_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that if a user tries to unreact
    with a react_id which they have not used on
    a message in a dm, an input error is raised.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message_id = response.json()

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == InputError.code


def test_not_member_of_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to react
    to a message in a channel they are not a member
    of, an AccessError is raised.
    '''
    user_1, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_1["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD",
                                   "name_first": "Will", "name_last": "Jones"})
    user_2 = response.json()

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})

    assert response.status_code == InputError.code


def test_not_member_of_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that if a user tries to react
    to a message in a dm they are not a member
    of, an AccessError is raised.
    '''
    user_1, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user_1["token"], "dm_id": dm["dm_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "james.smith@unsw.edu.au", "password": "GREATPASSWORD",
                                   "name_first": "James", "name_last": "Smith"})
    user_2 = response.json()

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})

    assert response.status_code == InputError.code


def test_two_users_react_unreact_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that two users can unreact
    to a particular message in a channel.
    '''
    user_1, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD",
                                   "name_first": "Will", "name_last": "Jones"})
    user_2 = response.json()

    requests.post(f"{BASE_URL}/channel/join/v2",
                  json={"token": user_2["token"], "channel_id": channel["channel_id"]})

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_1["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_id = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_1["token"], "message_id": message_id["message_id"],
                        "react_id": react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_2["token"], "message_id": message_id["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_1["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200


def test_two_users_unreact_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that two users can unreact
    to a particular message in a dm.
    '''
    user_1, user_2, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user_1["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message_id = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_1["token"], "message_id": message_id["message_id"],
                        "react_id": react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_2["token"], "message_id": message_id["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_1["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message_id["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200


def test_two_consecutive_unreacts_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that a user can unreact
    to two different messages consecutively.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": "Hello"})
    message_1 = response.json()

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": "Hello again"})
    message_2 = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user["token"], "message_id": message_1["message_id"],
                        "react_id": react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user["token"], "message_id": message_2["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_1["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_2["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200


def test_two_consecutive_unreacts_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that a user can unreact
    to two different messages consecutively.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message_1 = response.json()

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello again"})
    message_2 = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user["token"], "message_id": message_1["message_id"],
                        "react_id": react_id})

    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user["token"], "message_id": message_2["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_1["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user["token"], "message_id": message_2["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200


def test_unreact_someone_else_message_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that a user can unreact
    to their own react on someone else's
    messages in a channel.
    '''
    user_1, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD",
                                   "name_first": "Will", "name_last": "Jones"})
    user_2 = response.json()

    requests.post(f"{BASE_URL}/channel/join/v2",
                  json={"token": user_2["token"], "channel_id": channel["channel_id"]})

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_1["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message_1 = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_2["token"], "message_id": message_1["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message_1["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200


def test_unreact_someone_else_message_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that a user can unreact
    to their own react on someone else's
    messages in a dm.
    '''
    user_1, user_2, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user_1["token"], "dm_id": dm["dm_id"],
                                   "message": f"Hello"})
    message = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_2["token"], "message_id": message["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message["message_id"],
                                   "react_id": react_id})
    assert response.status_code == 200


def test_unreact_someone_else_react_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to
    unreact to someone else's react in a
    channel, an input error is raised.
    '''
    user_1, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "will.jones@unsw.edu.au", "password": "PASSWORD",
                                   "name_first": "Will", "name_last": "Jones"})
    user_2 = response.json()

    requests.post(f"{BASE_URL}/channel/join/v2",
                  json={"token": user_2["token"], "channel_id": channel["channel_id"]})

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_1["token"], "channel_id": channel["channel_id"],
                                   "message": f"Hello"})
    message = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_1["token"], "message_id": message["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message["message_id"],
                                   "react_id": react_id})
    assert response.status_code == InputError.code


def test_unreact_someone_else_react_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that if a user tries to
    unreact to someone else's react in a
    dm, an input error is raised.
    '''
    user_1, user_2, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user_1["token"], "dm_id": dm["dm_id"],
                                   "message": f"Hello"})
    message = response.json()

    react_id = 1
    requests.post(f"{BASE_URL}/message/react/v1",
                  json={"token": user_1["token"], "message_id": message["message_id"],
                        "react_id": react_id})

    response = requests.post(f"{BASE_URL}/message/unreact/v1",
                             json={"token": user_2["token"], "message_id": message["message_id"],
                                   "react_id": react_id})
    assert response.status_code == InputError.code

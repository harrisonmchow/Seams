'''
This test fle aims to validate the functionality of the message/react/v1
http route using pytest.

Functions:
    clear_register_user_and_create_channel()
    clear_register_users_and_create_dm()
    test_valid_input_channel_id()
    test_valid_input_dm_id()
    test_both_dm_id_channel_id_invalid()
    test_neither_id_neg1()
    test_invalid_og_message_id()
    test_msg_length_over_1000_channel()
    test_msg_length_over_1000_dm()
    test_msg_length_of_1000_channel()
    test_msg_length_of_1000_dm()
    test_not_joined_channel_sharing_to()
    test_not_joined_dm_sharing_to()
    test_two_messages_share_second_dm()
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


def test_valid_input_channel_id(clear_register_user_and_create_channel):
    '''
    This test verifies that if valid input is
    entered with a valid channel_id, the route
    returns a 200 status code and the return
    types are correct.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": "Hello"})
    message = response.json()
    assert response.status_code == 200

    dm_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": channel["channel_id"], "dm_id": dm_id})
    response_data = response.json()
    assert response.status_code == 200
    assert isinstance(response_data, dict) is True
    assert isinstance(response_data['shared_message_id'], int) is True


def test_valid_input_dm_id(clear_register_users_and_create_dm):
    '''
    This test verifies that if valid input is
    entered with a valid dm_id, the route
    returns a 200 status code and the return
    types are correct.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    channel_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": channel_id, "dm_id": dm["dm_id"]})
    response_data = response.json()
    assert response.status_code == 200
    assert isinstance(response_data, dict) is True
    assert isinstance(response_data['shared_message_id'], int) is True


def test_both_dm_id_channel_id_invalid(clear_register_users_and_create_dm):
    '''
    This test verifies that if both the dm_id
    and channel_id are invlaid, an InputError
    is raised.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    invalid_channel_id = 2
    invalid_dm_id = 2
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": invalid_channel_id, "dm_id": invalid_dm_id})
    assert response.status_code == InputError.code


def test_neither_id_neg1(clear_register_users_and_create_dm):
    '''
    This test verifies that if neither the dm_id
    or channel_id are -1 then an InputError is
    raised.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/channels/create/v2",
                             json={"token": user['token'], "name": "Badger Channel", "is_public": True})
    channel = response.json()

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": channel["channel_id"], "dm_id": dm["dm_id"]})
    assert response.status_code == InputError.code


def test_invalid_og_message_id(clear_register_user_and_create_channel):
    '''
    This test verifies that if the og_message_id
    is invalid, an InputError is raised.
    '''
    user, channel = clear_register_user_and_create_channel

    requests.post(f"{BASE_URL}/message/send/v1",
                  json={"token": user["token"], "channel_id": channel["channel_id"],
                        "message": "Hello"})

    invalid_msg_id = 2
    dm_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": invalid_msg_id,
                                   "message": "Hello Everyone", "channel_id": channel["channel_id"], "dm_id": dm_id})
    assert response.status_code == InputError.code


def test_msg_length_over_1000_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that if the length of the
    new message being sent to a channel is over
    1000 characters, an InputError is raised.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": "Hello"})
    message = response.json()

    dm_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": 'ABuL0wE7b963KVgEg5OQ2dud483B5C8vJX0Z2K8WW7CGJVrZnopeAiBdf9qrNG5XDkJumgg4n6j'
                                   'kaZVEyoPsFMsIBRDHXnJDXRD7RlKqPIEm5Ct6rQanzBL84fDiIGOZARPAOBzf5d32NjeVXSh9KczVPSqRS'
                                   '0FLZun6E1p4HJRt6NYCa37KjxQU4Aj6jCLNIkyuxc239R83K3GcyhYbOBrBGgTEDybfQo6fyF0VVj1VOc0'
                                   'TTpXBLR1K5tJk5L6ImrBKrEEudtety50qIsExp0yAYST1cFzrhDhJLlciXjMiJ50OEqIwQJSEKX8cMMIi'
                                   'CrO5AW1cPsPbR1unKfrCY7PHBIrVM6rtEMppZKXHUW5RCCMGE2vkFT2nLfmXbfb7DwolAvexr4hs13je3'
                                   'kkf1F1Gx3dmsgkZDPfglgKW8gak7wimzcHSKYlrhkVq2gJPT0vgdzmBnidQfl0K7hXlAkA1pzyVx7alNP'
                                   'Rh6JUU78AVuG9PBTeI9A8e33tblPfoOEOBzJFKYZYwJrSjdZLUQXJ82QHFlcz62SYa1hIeFyNgteDnsRE'
                                   '9rQWukR4oM8fzyWMMJn7QtQNDehzzylQlkmcGMhnKhLs5WrpgJcvaOgxQncMF4nKCovYIHXWgxmqH3K4U'
                                   '3JIa1vn0lyfBwRce2sN9ehyDRRFacvBoF6o2BS1V9h2mMLzyhb6lixOdiuh3jFkMbrfR2n9jtO5cYFoZy'
                                   'hRbBNIGVzWtsSZEsl1e7C1Q5CG5lMOBCVcjDUbos2S4mHwOMMe0WzsoqohG51Uc58wHy4Sjs5SRdVajv1'
                                   'tV4gQ44eTckPxuyfs1XubtGttgKLuAHbq4TkokJPtITicN7AavuGSqwX5QTalUFfpiQazpunNASI02he3'
                                   'vjlz5DLvx8rIb0pomauQx5hf0P74xisdv51cGOKqerv5auZIeLpkK3tZUZeLUyO9ABZDeaV2SDhJuDmii'
                                   'JQLmtH1lRYqL1tIqvAYvvn6MmaweC68wE', "channel_id": channel["channel_id"], "dm_id": dm_id})
    assert response.status_code == InputError.code


def test_msg_length_over_1000_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that if the length of the
    new message being sent to a dm is over
    1000 characters, an InputError is raised.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    channel_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": 'ABuL0wE7b963KVgEg5OQ2dud483B5C8vJX0Z2K8WW7CGJVrZnopeAiBdf9qrNG5XDkJumgg4n6j'
                                   'kaZVEyoPsFMsIBRDHXnJDXRD7RlKqPIEm5Ct6rQanzBL84fDiIGOZARPAOBzf5d32NjeVXSh9KczVPSqRS'
                                   '0FLZun6E1p4HJRt6NYCa37KjxQU4Aj6jCLNIkyuxc239R83K3GcyhYbOBrBGgTEDybfQo6fyF0VVj1VOc0'
                                   'TTpXBLR1K5tJk5L6ImrBKrEEudtety50qIsExp0yAYST1cFzrhDhJLlciXjMiJ50OEqIwQJSEKX8cMMIi'
                                   'CrO5AW1cPsPbR1unKfrCY7PHBIrVM6rtEMppZKXHUW5RCCMGE2vkFT2nLfmXbfb7DwolAvexr4hs13je3'
                                   'kkf1F1Gx3dmsgkZDPfglgKW8gak7wimzcHSKYlrhkVq2gJPT0vgdzmBnidQfl0K7hXlAkA1pzyVx7alNP'
                                   'Rh6JUU78AVuG9PBTeI9A8e33tblPfoOEOBzJFKYZYwJrSjdZLUQXJ82QHFlcz62SYa1hIeFyNgteDnsRE'
                                   '9rQWukR4oM8fzyWMMJn7QtQNDehzzylQlkmcGMhnKhLs5WrpgJcvaOgxQncMF4nKCovYIHXWgxmqH3K4U'
                                   '3JIa1vn0lyfBwRce2sN9ehyDRRFacvBoF6o2BS1V9h2mMLzyhb6lixOdiuh3jFkMbrfR2n9jtO5cYFoZy'
                                   'hRbBNIGVzWtsSZEsl1e7C1Q5CG5lMOBCVcjDUbos2S4mHwOMMe0WzsoqohG51Uc58wHy4Sjs5SRdVajv1'
                                   'tV4gQ44eTckPxuyfs1XubtGttgKLuAHbq4TkokJPtITicN7AavuGSqwX5QTalUFfpiQazpunNASI02he3'
                                   'vjlz5DLvx8rIb0pomauQx5hf0P74xisdv51cGOKqerv5auZIeLpkK3tZUZeLUyO9ABZDeaV2SDhJuDmii'
                                   'JQLmtH1lRYqL1tIqvAYvvn6MmaweC68wE', "channel_id": channel_id, "dm_id": dm["dm_id"]})
    assert response.status_code == InputError.code


def test_msg_length_of_1000_channel(clear_register_user_and_create_channel):
    '''
    This test verifies that if the length of the
    new message being sent to a channel is
    1000 characters, status code is 200.
    '''
    user, channel = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user["token"], "channel_id": channel["channel_id"],
                                   "message": "Hello"})
    message = response.json()

    dm_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": 'ABuL0wE7b963KVgEg5OQ2dud483B5C8vJX0Z2K8WW7CGJVrZnopeAiBdf9qrNG5XDkJumgg4n6j'
                                   'kaZVEyoPsFMsIBRDHXnJDXRD7RlKqPIEm5Ct6rQanzBL84fDiIGOZARPAOBzf5d32NjeVXSh9KczVPSqRS'
                                   '0FLZun6E1p4HJRt6NYCa37KjxQU4Aj6jCLNIkyuxc239R83K3GcyhYbOBrBGgTEDybfQo6fyF0VVj1VOc0'
                                   'TTpXBLR1K5tJk5L6ImrBKrEEudtety50qIsExp0yAYST1cFzrhDhJLlciXjMiJ50OEqIwQJSEKX8cMMIi'
                                   'CrO5AW1cPsPbR1unKfrCY7PHBIrVM6rtEMppZKXHUW5RCCMGE2vkFT2nLfmXbfb7DwolAvexr4hs13je3'
                                   'kkf1F1Gx3dmsgkZDPfglgKW8gak7wimzcHSKYlrhkVq2gJPT0vgdzmBnidQfl0K7hXlAkA1pzyVx7alNP'
                                   'Rh6JUU78AVuG9PBTeI9A8e33tblPfoOEOBzJFKYZYwJrSjdZLUQXJ82QHFlcz62SYa1hIeFyNgteDnsRE'
                                   '9rQWukR4oM8fzyWMMJn7QtQNDehzzylQlkmcGMhnKhLs5WrpgJcvaOgxQncMF4nKCovYIHXWgxmqH3K4U'
                                   '3JIa1vn0lyfBwRce2sN9ehyDRRFacvBoF6o2BS1V9h2mMLzyhb6lixOdiuh3jFkMbrfR2n9jtO5cYFoZy'
                                   'hRbBNIGVzWtsSZEsl1e7C1Q5CG5lMOBCVcjDUbos2S4mHwOMMe0WzsoqohG51Uc58wHy4Sjs5SRdVajv1'
                                   'tV4gQ44eTckPxuyfs1XubtGttgKLuAHbq4TkokJPtITicN7AavuGSqwX5QTalUFfpiQazpunNASI02he3'
                                   'vjlz5DLvx8rIb0pomauQx5hf0P74xisdv51cGOKqerv5auZIeLpkK3tZUZeLUyO9ABZDeaV2SDhJuDmii'
                                   'JQLmtH1lRYqL1tIqvAYvvn6MmaweC68w', "channel_id": channel["channel_id"], "dm_id": dm_id})
    assert response.status_code == 200


def test_msg_length_of_1000_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that if the length of the
    new message being sent to a dm is
    1000 characters, status code is 200.
    '''
    user, _, dm = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    channel_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user["token"], "og_message_id": message['message_id'],
                                   "message": 'ABuL0wE7b963KVgEg5OQ2dud483B5C8vJX0Z2K8WW7CGJVrZnopeAiBdf9qrNG5XDkJumgg4n6j'
                                   'kaZVEyoPsFMsIBRDHXnJDXRD7RlKqPIEm5Ct6rQanzBL84fDiIGOZARPAOBzf5d32NjeVXSh9KczVPSqRS'
                                   '0FLZun6E1p4HJRt6NYCa37KjxQU4Aj6jCLNIkyuxc239R83K3GcyhYbOBrBGgTEDybfQo6fyF0VVj1VOc0'
                                   'TTpXBLR1K5tJk5L6ImrBKrEEudtety50qIsExp0yAYST1cFzrhDhJLlciXjMiJ50OEqIwQJSEKX8cMMIi'
                                   'CrO5AW1cPsPbR1unKfrCY7PHBIrVM6rtEMppZKXHUW5RCCMGE2vkFT2nLfmXbfb7DwolAvexr4hs13je3'
                                   'kkf1F1Gx3dmsgkZDPfglgKW8gak7wimzcHSKYlrhkVq2gJPT0vgdzmBnidQfl0K7hXlAkA1pzyVx7alNP'
                                   'Rh6JUU78AVuG9PBTeI9A8e33tblPfoOEOBzJFKYZYwJrSjdZLUQXJ82QHFlcz62SYa1hIeFyNgteDnsRE'
                                   '9rQWukR4oM8fzyWMMJn7QtQNDehzzylQlkmcGMhnKhLs5WrpgJcvaOgxQncMF4nKCovYIHXWgxmqH3K4U'
                                   '3JIa1vn0lyfBwRce2sN9ehyDRRFacvBoF6o2BS1V9h2mMLzyhb6lixOdiuh3jFkMbrfR2n9jtO5cYFoZy'
                                   'hRbBNIGVzWtsSZEsl1e7C1Q5CG5lMOBCVcjDUbos2S4mHwOMMe0WzsoqohG51Uc58wHy4Sjs5SRdVajv1'
                                   'tV4gQ44eTckPxuyfs1XubtGttgKLuAHbq4TkokJPtITicN7AavuGSqwX5QTalUFfpiQazpunNASI02he3'
                                   'vjlz5DLvx8rIb0pomauQx5hf0P74xisdv51cGOKqerv5auZIeLpkK3tZUZeLUyO9ABZDeaV2SDhJuDmii'
                                   'JQLmtH1lRYqL1tIqvAYvvn6MmaweC68w', "channel_id": channel_id, "dm_id": dm["dm_id"]})
    assert response.status_code == 200


def test_not_joined_channel_sharing_to(clear_register_user_and_create_channel):
    '''
    This test verifies that if a user tries to share
    a message to a channel they have not joined, an
    AccessError is raised.
    '''
    user_1, _ = clear_register_user_and_create_channel

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "james.smith@unsw.edu.au", "password": "PASSSWORD",
                                   "name_first": "James", "name_last": "Smith"})
    user_2 = response.json()

    response = requests.post(f"{BASE_URL}/channels/create/v2",
                             json={"token": user_2['token'], "name": "Panther Channel", "is_public": True})
    channel_2 = response.json()

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={"token": user_2["token"], "channel_id": channel_2["channel_id"],
                                   "message": "Hello"})
    message = response.json()

    dm_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user_1["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": channel_2['channel_id'], "dm_id": dm_id})

    assert response.status_code == AccessError.code


def test_not_joined_dm_sharing_to(clear_register_users_and_create_dm):
    '''
    The test verifies that if a user tries to share
    a message to a dm they have not joined, an
    AccessError is raised.
    '''
    user_1, user_2, _ = clear_register_users_and_create_dm

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "nick.smith@unsw.edu.au", "password": "PASSSWORD",
                                   "name_first": "Nick", "name_last": "Smith"})
    user_3 = response.json()

    response = requests.post(f"{BASE_URL}/dm/create/v1",
                             json={"token": user_2['token'], "u_ids": [user_3['auth_user_id']]})
    dm_2 = response.json()

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user_3["token"], "dm_id": dm_2["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    channel_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user_1["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": channel_id, "dm_id": dm_2['dm_id']})

    assert response.status_code == AccessError.code


def test_two_messages_share_second_dm(clear_register_users_and_create_dm):
    '''
    This test verifies that the function operates
    correctly when more than one messages is sent
    and the second is shared.
    '''
    user_1, user_2, dm = clear_register_users_and_create_dm

    requests.post(f"{BASE_URL}/message/senddm/v1",
                  json={"token": user_1["token"], "dm_id": dm["dm_id"],
                        "message": "Hello"})

    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={"token": user_2["token"], "dm_id": dm["dm_id"],
                                   "message": "Hello"})
    message = response.json()

    channel_id = -1
    response = requests.post(f"{BASE_URL}/message/share/v1",
                             json={"token": user_1["token"], "og_message_id": message['message_id'],
                                   "message": "Hello Everyone", "channel_id": channel_id, "dm_id": dm['dm_id']})

    assert response.status_code == 200

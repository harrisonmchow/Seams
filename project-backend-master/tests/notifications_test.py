"""
This module aims to test the functionalitiy of generate_notifications, generate_tag and get_notifications. 

Functions:
    test_tag_ch_success ()
    test_tag_dm_success ()
    test_tag_long_message ()
    test_message_edit ()
    test_several_tags ()
    test_double_tag ()
    test_tag_position ()
    test_word_and_tag_combined ()
    test_no_tag ()
    test_react_success ()
    test_channel_inv_success ()
    test_dm_invite_success ()
    test_get_notifications ()
    test_get_notifications2 ()
    test_several_invitees ()
"""
import pytest
import requests
from datetime import datetime, timedelta

from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_and_create_channel():
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']

    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": "channel1", "is_public": True})
    assert response_input.status_code == 200
    channel_id = response_input.json()

    response2 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "jack@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "jack", "name_last": "adams"})
    assert response2.status_code == 200
    data = response2.json()
    token2 = data['token']
    id = data['auth_user_id']

    ch_id = channel_id['channel_id']
    response3 = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": token, "channel_id": ch_id, "u_id": id})
    assert response3.status_code == 200

    return token, id, ch_id, token2


@pytest.fixture
def clear_register_and_create_dm():
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']
    id = data['auth_user_id']

    response1 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "jack@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "jack", "name_last": "adams"})
    assert response1.status_code == 200
    data = response1.json()
    token2 = data['token']
    id2 = data['auth_user_id']

    response_input = requests.post(
        f"{BASE_URL}/dm/create/v1", json={"token": token, "u_ids": [id2]})
    assert response_input.status_code == 200

    data = response_input.json()
    dm_id = data['dm_id']

    return token, id, dm_id, token2


@pytest.fixture
def clear_register_and_create_channel_4_users():
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']

    response_input = requests.post(f"{BASE_URL}/channels/create/v2", json={"token": token,
                                                                           "name": "channel1", "is_public": True})
    assert response_input.status_code == 200
    channel_id = response_input.json()
    ch_id = channel_id['channel_id']

    response2 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "jack@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "jack", "name_last": "adams"})
    assert response2.status_code == 200
    data = response2.json()
    token2 = data['token']
    id_jack = data['auth_user_id']

    response6 = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": token, "channel_id": ch_id, "u_id": id_jack})
    assert response6.status_code == 200

    response3 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "james", "name_last": "pinnington"})
    assert response3.status_code == 200
    data = response3.json()
    token_james = data['token']
    id_james = data['auth_user_id']

    response7 = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": token, "channel_id": ch_id, "u_id": id_james})
    assert response7.status_code == 200

    response4 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "felix@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "felix", "name_last": "li"})
    assert response4.status_code == 200
    data = response4.json()
    token_felix = data['token']
    id_felix = data['auth_user_id']

    response7 = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": token, "channel_id": ch_id, "u_id": id_felix})
    assert response7.status_code == 200

    response5 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "gerard@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "gerard", "name_last": "mathews"})
    assert response5.status_code == 200
    data = response5.json()
    token_gerard = data['token']
    id_gerard = data['auth_user_id']

    response7 = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": token, "channel_id": ch_id, "u_id": id_gerard})
    assert response7.status_code == 200

    return token, id_jack, ch_id, token2, token_james, token_felix, token_gerard


def test_tag_ch_success(clear_register_and_create_channel):  # call get notifications
    '''
    tags a user in a channel
    '''
    token = clear_register_and_create_channel[0]
    token2 = clear_register_and_create_channel[3]
    channel_id = clear_register_and_create_channel[2]
    message = "Hey there @jackadams"

    response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                   "channel_id": channel_id, "message": message})
    assert response1.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}, {
        'channel_id': 1,  'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hey there @jackadams'}]


def test_tag_dm_success(clear_register_and_create_dm):
    '''
    tags a user in a dm
    '''
    token = clear_register_and_create_dm[0]
    token2 = clear_register_and_create_dm[3]
    dm_id = clear_register_and_create_dm[2]

    response1 = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                     "dm_id": dm_id, "message": "Hey there @jackadams"})
    assert response1.status_code == 200
    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow added you to harrychow, jackadams'}, {
        'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow tagged you in harrychow, jackadams: Hey there @jackadams'}]


def test_tag_long_message(clear_register_and_create_dm):
    '''
    tags a user in a dm message longer than 20 characters
    '''
    token = clear_register_and_create_dm[0]
    token2 = clear_register_and_create_dm[3]
    dm_id = clear_register_and_create_dm[2]

    response1 = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                     "dm_id": dm_id, "message": "Hi @jackadams why does this happen?"})
    assert response1.status_code == 200
    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow added you to harrychow, jackadams'}, {
        'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow tagged you in harrychow, jackadams: Hi @jackadams why do'}]


def test_message_edit(clear_register_and_create_channel):
    '''
    Edits a message to include a tag
    '''
    token = clear_register_and_create_channel[0]
    channel_id = clear_register_and_create_channel[2]
    message = "Hi there jackadams"
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel_id, "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    message_id = data['message_id']

    print(message_id)

    new_message = "Hi there @jackadams"
    response_input = requests.put(f"{BASE_URL}/message/edit/v1", json={"token": token,
                                                                       "message_id": message_id, "message": new_message})
    assert response_input.status_code == 200


# if user doesnt exist nothing done
def test_several_tags(clear_register_and_create_channel_4_users):
    '''
    Tags several users in one channel message
    '''
    token = clear_register_and_create_channel_4_users[0]
    token_jack = clear_register_and_create_channel_4_users[3]
    token_felix = clear_register_and_create_channel_4_users[5]
    channel_id = clear_register_and_create_channel_4_users[2]
    message = "Hey there @jackadams and @felixli"

    response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                   "channel_id": channel_id, "message": message})
    assert response1.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_jack})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [
        {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hey there @jackadams'}]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_felix})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}, {
        'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hey there @jackadams'}]


def test_double_tag(clear_register_and_create_channel_4_users):
    '''
    Tags two users in the same word (unseparated by white-space)
    '''
    token = clear_register_and_create_channel_4_users[0]
    token_jack = clear_register_and_create_channel_4_users[3]
    token_felix = clear_register_and_create_channel_4_users[5]
    channel_id = clear_register_and_create_channel_4_users[2]
    message = "Hey there @jackadams@felixli"

    response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                   "channel_id": channel_id, "message": message})
    assert response1.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_jack})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [
        {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hey there @jackadams'}]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_felix})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}, {
        'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hey there @jackadams'}]


def test_tag_position(clear_register_and_create_dm):
    '''
    tags user at the start of a message
    '''
    token = clear_register_and_create_dm[0]
    token2 = clear_register_and_create_dm[3]
    dm_id = clear_register_and_create_dm[2]

    response1 = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                     "dm_id": dm_id, "message": "@jackadams"})
    assert response1.status_code == 200
    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow added you to harrychow, jackadams'}, {
        'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow tagged you in harrychow, jackadams: @jackadams'}]


def test_word_and_tag_combined(clear_register_and_create_channel):
    '''
    tags a user in with a word unseparated froma handle by a white-space
    '''
    token = clear_register_and_create_channel[0]
    token2 = clear_register_and_create_channel[3]
    channel_id = clear_register_and_create_channel[2]
    message = "Hey there@jackadams"

    response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                   "channel_id": channel_id, "message": message})
    assert response1.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}, {
        'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hey there@jackadams'}]


def test_no_tag(clear_register_and_create_channel):
    '''
    No tag in message creating no notification
    '''
    token = clear_register_and_create_channel[0]
    token2 = clear_register_and_create_channel[3]
    channel_id = clear_register_and_create_channel[2]
    message = "Hey there jackadams"

    response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                   "channel_id": channel_id, "message": message})
    assert response1.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [
        {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}]


# react notifications

def test_react_success(clear_register_and_create_channel):
    '''
    Tests the react notification of user 2
    '''
    token = clear_register_and_create_channel[0]
    token2 = clear_register_and_create_channel[3]
    channel_id = clear_register_and_create_channel[2]
    message = "Hey there jackadams"

    response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                   "channel_id": channel_id, "message": message})
    assert response1.status_code == 200
    data = response1.json()
    message_id = data['message_id']

    react_id = 1
    response = requests.post(f"{BASE_URL}/message/react/v1",
                             json={"token": token2, "message_id": message_id,
                                   "react_id": react_id})
    assert response.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    # the person who reacted to the message gets no react message
    assert notifications == [
        {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [
        {'channel_id': 1, 'dm_id': -1, 'notification_message': 'jackadams reacted to your message in channel1'}]

# channel/dm notifications


def test_channel_inv_success(clear_register_and_create_channel):
    '''
    Success case for channel invite
    '''
    token2 = clear_register_and_create_channel[3]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [
        {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow added you to channel1'}]


def test_dm_invite_success(clear_register_and_create_dm):
    '''
    Success case for dm invite
    '''
    token2 = clear_register_and_create_dm[3]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1,
                              'notification_message': 'harrychow added you to harrychow, jackadams'}]


def test_get_notifications(clear_register_and_create_channel):
    '''
    Gets the last 20 notifications of a user
    '''
    token = clear_register_and_create_channel[0]
    token2 = clear_register_and_create_channel[3]
    channel_id = clear_register_and_create_channel[2]
    message = "Hi @jackadams"

    i = 0
    while i < 21:
        response1 = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                       "channel_id": channel_id, "message": message + " " + str(i)})
        assert response1.status_code == 200
        i += 1

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 1'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 2'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 3'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 4'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 5'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 6'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 7'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 8'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 9'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 10'}, {
        'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 11'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 12'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 13'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 14'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 15'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 16'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 17'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 18'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 19'}, {'channel_id': 1, 'dm_id': -1, 'notification_message': 'harrychow tagged you in channel1: Hi @jackadams 20'}]


def test_get_notifications2():
    '''
    Gets no notifications 
    '''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']

    assert notifications == []


def test_several_invitees():
    '''
    Creates notifications for several initees
    '''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "harry@unsw.edu.au",
                                                                   "password": "Password12345", "name_first": "harry", "name_last": "chow"})
    assert response.status_code == 200
    data = response.json()
    token = data['token']

    response2 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "jack@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "jack", "name_last": "adams"})
    assert response2.status_code == 200
    data = response2.json()
    token2 = data['token']
    id_jack = data['auth_user_id']

    response3 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "james@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "james", "name_last": "pinnington"})
    assert response3.status_code == 200
    data = response3.json()
    token_james = data['token']
    id_james = data['auth_user_id']

    response4 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "felix@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "felix", "name_last": "li"})
    assert response4.status_code == 200
    data = response4.json()
    token_felix = data['token']
    id_felix = data['auth_user_id']

    response5 = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": "gerard@unsw.edu.au",
                                                                    "password": "Password1", "name_first": "gerard", "name_last": "mathews"})
    assert response5.status_code == 200
    data = response5.json()
    token_gerard = data['token']
    id_gerard = data['auth_user_id']

    response_input = requests.post(
        f"{BASE_URL}/dm/create/v1", json={"token": token, "u_ids": [id_jack, id_james, id_felix, id_gerard]})
    assert response_input.status_code == 200

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token2})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [
        {'channel_id': -1, 'dm_id': 1, 'notification_message': 'harrychow added you to felixli, gerardmathews, harrychow, jackadams, jamespinnington'}]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_james})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1,
                              'notification_message': 'harrychow added you to felixli, gerardmathews, harrychow, jackadams, jamespinnington'}]

    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_felix})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1,
                              'notification_message': 'harrychow added you to felixli, gerardmathews, harrychow, jackadams, jamespinnington'}]
    response = requests.get(
        f"{BASE_URL}/notifications/get/v1", params={'token': token_gerard})
    assert response.status_code == 200
    data = response.json()
    notifications = data['notifications']
    assert notifications == [{'channel_id': -1, 'dm_id': 1,
                              'notification_message': 'harrychow added you to felixli, gerardmathews, harrychow, jackadams, jamespinnington'}]

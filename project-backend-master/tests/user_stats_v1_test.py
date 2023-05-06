'''
This test file aims to validate the functionaility of user/stats/v1 and the front end. 

Functions:
    clear
    register_and_login1
    register_and_login2
    create_channel
    create_dm
    send_message_channel
    send_message_dm

    test_invalid_token
    test_invalid_token_format
    test_nothing
    test_channel_create_and_msg_sent
    test_dm_create_then_remove
    test_involvement_rate
    test_involvement_rate_greater_than_1
'''

from src.user import user_stats_v1
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

    channel_id = response_input.json()['channel_id']
    return channel_id


def create_dm(token, u_ids):
    response = requests.post(f"{BASE_URL}/dm/create/v1", json={"token": token,
                                                               "u_ids": u_ids})
    assert response.status_code == 200
    dm_id = response.json()['dm_id']
    return dm_id


def send_msg_channel(token, channel_id, message):
    response_input = requests.post(f"{BASE_URL}/message/send/v1", json={"token": token,
                                                                        "channel_id": channel_id, "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    return data['message_id']


def send_msg_dm(token, dm_id, message):
    response_input = requests.post(f"{BASE_URL}/message/senddm/v1", json={"token": token,
                                                                          "dm_id": dm_id, "message": message})
    assert response_input.status_code == 200
    data = response_input.json()
    return data['message_id']

# --------------------------------------------------------------------------------------------------


def test_invalid_token(clear):
    invalid_token = encode_token(-1)
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": invalid_token})
    assert response.status_code == AccessError.code


def test_invalid_token_format(clear):
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": -1})
    assert response.status_code == AccessError.code


def test_nothing(clear, register_and_login1):
    token = register_and_login1[0]
    time = int(datetime.timestamp(datetime.now()))
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token})
    assert response.status_code == 200
    data = response.json()['user_stats']

    channel_list = data['channels_joined']
    assert len(channel_list) == 1
    # channel_expected = {'num_channels_joined': 0, 'time_stamp': time}
    assert channel_list[0]['num_channels_joined'] == 0
    exp_time = channel_list[0]['time_stamp']
    assert abs(exp_time - time) <= 1

    dm_list = data['dms_joined']
    assert len(dm_list) == 1
    # dm_expected = {'num_dms_joined': 0, 'time_stamp': time}
    assert dm_list[0]['num_dms_joined'] == 0
    exp_time = dm_list[0]['time_stamp']
    assert abs(exp_time - time) <= 1

    involvement_rate = data['involvement_rate']
    assert involvement_rate == 0

    message_list = data['messages_sent']
    assert len(message_list) == 1
    # message_expected = {'num_messages_sent': 0, 'time_stamp': time}
    assert message_list[0]['num_messages_sent'] == 0
    exp_time = message_list[0]['time_stamp']
    assert abs(exp_time - time) <= 1


def test_channel_create_and_msg_sent(clear, register_and_login1):
    token = register_and_login1[0]
    time1 = int(datetime.timestamp(datetime.now()))

    time.sleep(0.5)
    ch_id = create_channel(token, "Channel 1", True)
    time2 = int(datetime.timestamp(datetime.now()))

    time.sleep(0.3)
    send_msg_channel(token, ch_id, "Hello")
    time3 = int(datetime.timestamp(datetime.now()))

    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token})
    assert response.status_code == 200
    data = response.json()['user_stats']

    channel_list = data['channels_joined']
    assert len(channel_list) == 2
    # expected: channels_list = [{'num_channels_joined': 0, 'time_stamp': time1},
    #                           {'num_channels_joined': 1, 'time_stamp': time2}]
    assert channel_list[0]['num_channels_joined'] == 0
    actual_time1 = channel_list[0]['time_stamp']
    assert abs(actual_time1 - time1) <= 1

    assert channel_list[1]['num_channels_joined'] == 1
    actual_time2 = channel_list[1]['time_stamp']
    assert abs(actual_time2 - time2) <= 1

    dm_list = data['dms_joined']
    assert len(dm_list) == 1
    # dm_expected = {'num_dms_joined': 0, 'time_stamp': time1}
    # assert dm_list[0] == dm_expected

    involvement_rate = data['involvement_rate']
    assert involvement_rate == 1

    message_list = data['messages_sent']
    assert len(message_list) == 2
    # expected: message_list = [{'num_messages_sent': 0, 'time_stamp': time1},
    #                           {'num_messages_sent': 1, 'time_stamp': time3}]
    # assert message_list[0] == message_expected
    assert message_list[0]['num_messages_sent'] == 0
    actual_time1 = message_list[0]['time_stamp']
    assert abs(actual_time1 - time1) <= 1

    assert message_list[1]['num_messages_sent'] == 1
    actual_time3 = message_list[1]['time_stamp']
    assert abs(actual_time3 - time3) <= 1


def test_dm_create_then_remove(clear, register_and_login1, register_and_login2):
    token = register_and_login1[0]
    time1 = int(datetime.timestamp(datetime.now()))
    token2, id2 = register_and_login2
    time2 = int(datetime.timestamp(datetime.now()))
    time.sleep(0.3)
    dm_id = create_dm(token, [id2])
    time3 = int(datetime.timestamp(datetime.now()))
    time.sleep(0.7)
    # send a msg to the dm
    send_msg_dm(token2, dm_id, "test")
    time4 = int(datetime.timestamp(datetime.now()))
    # delete the dm
    time.sleep(0.9)
    delete_response = requests.delete(
        f"{BASE_URL}/dm/remove/v1", json={"token": token, "dm_id": dm_id})
    time5 = int(datetime.timestamp(datetime.now()))
    assert delete_response.status_code == 200

    # user stats for the first user
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token})
    assert response.status_code == 200
    data = response.json()['user_stats']

    dm_list = data['dms_joined']
    # 3 elements, when user was first created, when dm was created, when dm was removed
    assert len(dm_list) == 3
    assert dm_list[0]['num_dms_joined'] == 0
    expected_time1 = dm_list[0]['time_stamp']
    assert abs(expected_time1 - time1) <= 1

    assert dm_list[1]['num_dms_joined'] == 1
    expected_time3 = dm_list[1]['time_stamp']
    assert abs(expected_time3 - time3) <= 1

    assert dm_list[2]['num_dms_joined'] == 0
    expected_time5 = dm_list[2]['time_stamp']
    assert abs(expected_time5 - time5) <= 1

    involvement = data['involvement_rate']
    assert involvement == 0

    # user stats for the second user
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token2})
    assert response.status_code == 200
    data = response.json()['user_stats']

    dm_list = data['dms_joined']
    # 3 elements, when user was first created, when dm was created, when dm was removed
    assert len(dm_list) == 3
    assert dm_list[0]['num_dms_joined'] == 0
    expected_time2 = dm_list[0]['time_stamp']
    assert abs(expected_time2 - time2) <= 1

    assert dm_list[1]['num_dms_joined'] == 1
    expected_time3 = dm_list[1]['time_stamp']
    assert abs(expected_time3 - time3) <= 1

    assert dm_list[2]['num_dms_joined'] == 0
    expected_time5 = dm_list[2]['time_stamp']
    assert abs(expected_time5 - time5) <= 1

    msg_list = data['messages_sent']
    # 2 elements, when user was first created, and when they sent msg to dm
    assert len(msg_list) == 2
    assert msg_list[0]['num_messages_sent'] == 0
    expected_time2 = msg_list[0]['time_stamp']
    assert abs(expected_time2 - time2) <= 1

    assert msg_list[1]['num_messages_sent'] == 1
    expected_time4 = msg_list[1]['time_stamp']
    assert abs(expected_time4 - time4) <= 1

    # since we removed the dm, the message that we sent before isn't counted
    involvement = data['involvement_rate']
    assert involvement == 0


def test_involvement_rate(clear, register_and_login1, register_and_login2):
    token = register_and_login1[0]
    token2, id2 = register_and_login2
    dm_id = create_dm(token, [id2])
    ch_id = create_channel(token2, "Ch1", True)
    time.sleep(0.3)
    send_msg_dm(token2, dm_id, "message1")
    time1 = int(datetime.timestamp(datetime.now()))
    time.sleep(0.6)
    send_msg_dm(token, dm_id, "message2")
    time2 = int(datetime.timestamp(datetime.now()))
    time.sleep(0.7)
    send_msg_channel(token2, ch_id, "message3")
    time3 = int(datetime.timestamp(datetime.now()))

    # user stats for the first user
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token})
    assert response.status_code == 200
    data = response.json()['user_stats']
    msg_list = data['messages_sent']
    assert msg_list[-1]['num_messages_sent'] == 1
    expected_time2 = msg_list[-1]['time_stamp']
    assert abs(expected_time2 - time2) <= 1

    exp_involvement = (1+1)/(1+1+3)
    assert exp_involvement == data['involvement_rate']

    # user stats for the second user
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token2})
    assert response.status_code == 200
    data = response.json()['user_stats']
    msg_list = data['messages_sent']

    assert msg_list[-2]['num_messages_sent'] == 1
    expected_time1 = msg_list[-2]['time_stamp']
    assert abs(expected_time1 - time1) <= 1

    assert msg_list[-1]['num_messages_sent'] == 2
    expected_time3 = msg_list[-1]['time_stamp']
    assert abs(expected_time3 - time3) <= 1

    exp_involvement2 = (1+1+2)/(1+1+3)
    assert exp_involvement2 == data['involvement_rate']


def test_involvement_rate_greater_than_1(clear, register_and_login1):
    token = register_and_login1[0]
    ch_id = create_channel(token, "Ch1", True)

    m1 = send_msg_channel(token, ch_id, "Message 1")
    send_msg_channel(token, ch_id, "Message 2")

    delete_response = requests.delete(
        f"{BASE_URL}/message/remove/v1", json={"token": token, "message_id": m1})

    assert delete_response.status_code == 200
    response = requests.get(f"{BASE_URL}/user/stats/v1",
                            params={"token": token})
    assert response.status_code == 200
    data = response.json()['user_stats']
    involvement = data['involvement_rate']
    assert involvement == 1
    # ch_joined = 1, msgs_sent = 2, dms_joined = 0
    # num_ch_exist = 1, num_msgs_exist = 1, num_dms_exist = 0
    # involvement = (3/2) = 1.5 = 1 (since it is capped at 1)

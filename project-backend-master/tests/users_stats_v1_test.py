'''
This test file aims to validate the functionaility of users/stats/v1 and the front end. 

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
    test_2_users_one_channel
    test_users_stats_dm_remove
    test_utilization_rate
    test_utilization_rate_after_user_removed

'''


# from re import T
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
    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": invalid_token})
    assert response.status_code == AccessError.code


def test_invalid_token_format(clear):
    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": -1})
    assert response.status_code == AccessError.code


def test_nothing(clear, register_and_login1):
    token = register_and_login1[0]
    now = int(datetime.timestamp(datetime.now()))

    time.sleep(0.4)
    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": token})
    assert response.status_code == 200

    data = response.json()['workspace_stats']
    ch_list = data['channels_exist']
    assert len(ch_list) == 1
    assert ch_list[0]['num_channels_exist'] == 0
    exp_time = ch_list[0]['time_stamp']
    assert abs(exp_time - now) <= 1

    dms_list = data['dms_exist']
    assert len(dms_list) == 1
    assert dms_list[0]['num_dms_exist'] == 0
    exp_time = dms_list[0]['time_stamp']
    assert abs(exp_time - now) <= 1

    msg_list = data['messages_exist']
    assert len(msg_list) == 1
    assert msg_list[0]['num_messages_exist'] == 0
    exp_time = msg_list[0]['time_stamp']
    assert abs(exp_time - now) <= 1

    assert data['utilization_rate'] == 0


def test_2_users_one_channel(clear, register_and_login1, register_and_login2):
    token1 = register_and_login1[0]
    time1 = int(datetime.timestamp(datetime.now()))
    time.sleep(0.3)
    ch_id = create_channel(token1, "Ch1", True)
    time2 = int(datetime.timestamp(datetime.now()))
    time.sleep(0.5)
    send_msg_channel(token1, ch_id, "This is the first message")
    time3 = int(datetime.timestamp(datetime.now()))

    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": token1})
    assert response.status_code == 200

    data = response.json()['workspace_stats']

    ch_list = data['channels_exist']
    assert ch_list[0]['num_channels_exist'] == 0
    exp_time1 = ch_list[0]['time_stamp']
    assert abs(exp_time1 - time1) <= 1

    assert ch_list[-1]['num_channels_exist'] == 1
    exp_time2 = ch_list[-1]['time_stamp']
    assert abs(exp_time2 - time2) <= 1

    msg_list = data['messages_exist']
    assert msg_list[-1]['num_messages_exist'] == 1
    exp_time3 = msg_list[-1]['time_stamp']
    assert abs(exp_time3 - time3) <= 1

    assert data['utilization_rate'] == 0.5


def test_users_stats_dm_remove(clear, register_and_login1, register_and_login2):
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    ch_id = create_channel(token1, "CH1", True)

    for i in [1, 2, 3]:
        send_msg_channel(token1, ch_id, f"message {i}")

    dm_id = create_dm(token1, [id2])
    time0 = int(datetime.timestamp(datetime.now()))
    times = []
    for i in [1, 2, 3]:
        send_msg_dm(token2, dm_id, f"message {i}")
        times.append(int(datetime.timestamp(datetime.now())))
        time.sleep(0.3)

    # remove the dm
    delete_response = requests.delete(
        f"{BASE_URL}/dm/remove/v1", json={"token": token1, "dm_id": dm_id})
    time1 = int(datetime.timestamp(datetime.now()))
    assert delete_response.status_code == 200

    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": token1})
    assert response.status_code == 200

    data = response.json()['workspace_stats']
    dm_list = data['dms_exist']
    assert dm_list[-2]['num_dms_exist'] == 1
    expected_time0 = dm_list[-2]['time_stamp']
    assert abs(expected_time0 - time0) <= 1

    assert dm_list[-1]['num_dms_exist'] == 0
    expected_time1 = dm_list[-1]['time_stamp']
    assert abs(expected_time1 - time1) <= 1

    msg_list = data['messages_exist']
    assert msg_list[-2]['num_messages_exist'] == 6
    exp_time = msg_list[-2]['time_stamp']
    assert abs(exp_time - times[2]) <= 1

    assert msg_list[-1]['num_messages_exist'] == 3
    exp_time1 = msg_list[-1]['time_stamp']
    assert abs(exp_time1 - time1) <= 1

    assert data['utilization_rate'] == 0.5


def test_utilization_rate(clear, register_and_login1, register_and_login2):
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2

    # create 4 users.
    token_list = []
    id_list = []
    for i in [1, 2, 3, 4]:
        response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": f"james{i}@unsw.edu.au",
                                                                       "password": "passworD1234655", "name_first": "James", "name_last": "Bob"})
        assert response.status_code == 200
        data = response.json()
        token = data['token']
        id = data['auth_user_id']
        token_list.append(token)
        id_list.append(id)

    create_dm(token1, [id2, id_list[2], id_list[3]])
    ch_id = create_channel(token2, "ch1", True)
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token_list[2], "channel_id": ch_id})
    assert response.status_code == 200

    create_channel(token_list[2], "ch2", False)

    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": token1})
    assert response.status_code == 200
    data = response.json()['workspace_stats']
    assert data['utilization_rate'] == 4/6


def test_utilization_rate_after_user_removed(clear, register_and_login1, register_and_login2):
    token1 = register_and_login1[0]
    token2, id2 = register_and_login2
    # create 4 users.
    token_list = []
    id_list = []
    for i in [1, 2, 3, 4]:
        response = requests.post(f"{BASE_URL}/auth/register/v2", json={"email": f"james{i}@unsw.edu.au",
                                                                       "password": "passworD1234655", "name_first": "James", "name_last": "Bob"})
        assert response.status_code == 200
        data = response.json()
        token = data['token']
        id = data['auth_user_id']
        token_list.append(token)
        id_list.append(id)

    create_dm(token1, [id2, id_list[2], id_list[3]])
    ch_id = create_channel(token2, "ch1", True)
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": token_list[2], "channel_id": ch_id})
    assert response.status_code == 200

    create_channel(token_list[2], "ch2", False)

    # remove a user.
    response = requests.delete(
        f"{BASE_URL}admin/user/remove/v1", json={"token": token1, "u_id": id_list[2]})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/users/stats/v1",
                            params={"token": token2})
    assert response.status_code == 200
    data = response.json()['workspace_stats']
    # token_list[0,1] not in
    assert data['utilization_rate'] == 3/5

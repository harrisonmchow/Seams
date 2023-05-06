'''
This test is designated for the standup/start/v1 function
It operates by taking in a valid jwt of a user
A channel id of an existing channel
and a length which indicates the length of the standup period
data_store will gain a new sub-object under

HTTP TEST for:
search_v1
'''

from src.error import InputError, AccessError
from src.config import url
import pytest
import requests
from datetime import datetime

BASE_URL = url


@pytest.fixture
def clear_register_and_reset_http():
    response = requests.delete(f'{BASE_URL}/clear/v1')
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                                 json = {'email': 'felix.li@vtub.er',
                                         'password': 'emptied',
                                         'name_first': 'felix',
                                         'name_last': 'li'})
    assert response.status_code == 200
    user = response.json()

    response = requests.post(f"{BASE_URL}/channels/create/v2",
                                 json = {'token': user['token'],
                                         'name': 'rizu_ch',
                                         'is_public': True})
    assert response.status_code == 200
    channel = response.json()

    return {
    	'user': user,
    	'channel': channel,
    }


def test_invalid_channel_id(clear_register_and_reset_http):
    '''
    If an invalid channel id is inputted, InputError should be triggered
    '''
    data = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': 9999,
                                         'length': 60})
    assert response.status_code == InputError.code


def test_invalid_time_length(clear_register_and_reset_http):
    '''
    If a negative length is inputted, InputError should be triggered
    '''
    data = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': -1})
    assert response.status_code == InputError.code


def test_standup_already_running(clear_register_and_reset_http):
    '''
    If another active standup is already running, InputError should be triggered
    '''
    data = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == InputError.code


def test_user_not_authorised(clear_register_and_reset_http):
    '''
    If channel id is valid but the user is not authorised, AccessError should be triggered
    '''
    data = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                                 json = {'email': 'nana.tatsudaki@vtub.er',
                                         'password': 'uuunotthis',
                                         'name_first': 'nana',
                                         'name_last': 'tatsudaki'})
    assert response.status_code == 200
    user_new = response.json()

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': user_new['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == AccessError.code


def test_start_general(clear_register_and_reset_http):
    '''
    General testing for output of the standup/start method
    '''
    data = clear_register_and_reset_http

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': data['user']['token'],
                                   'u_ids': []})
    assert response.status_code == 200
    new_dm = response.json()

    time_sent = datetime.timestamp(datetime.now()) + 10
    message = "Hello nice to meet you!"
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", 
                             json={"token": data['user']['token'],
                             'dm_id': new_dm['dm_id'], 'message': message, 'time_sent': time_sent})
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", 
                             json={"token": data['user']['token'],
                             'dm_id': new_dm['dm_id'], 'message': message, 'time_sent': time_sent + 1})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == 200

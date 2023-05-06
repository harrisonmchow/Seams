'''
This test is designated for the standup/start/v1 function
It operates by taking in a valid jwt of a user
and a channel id of an existing channel
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
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == 200
    
    response = requests.get(f"{BASE_URL}/standup/active/v1",
                                 params = {'token': data['user']['token'],
                                           'channel_id': 9999})
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
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/standup/active/v1",
                                 params = {'token': user_new['token'],
                                           'channel_id': data['channel']['channel_id']})
    assert response.status_code == AccessError.code


def test_not_running(clear_register_and_reset_http):
    '''
    If this channel has no active standups, it should return `None` for the time which this standup finishes
    '''
    data = clear_register_and_reset_http
    
    response = requests.get(f"{BASE_URL}/standup/active/v1",
                                 params = {'token': data['user']['token'],
                                           'channel_id': data['channel']['channel_id']})
    assert response.status_code == 200
    assert response.json()['time_finish'] == None


def test_active_general(clear_register_and_reset_http):
    '''
    General testing of standup/active
    '''
    data = clear_register_and_reset_http
    
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                                 json = {'email': 'ceres.fauna@holo.en',
                                         'password': 'uuunotthis',
                                         'name_first': 'ceres',
                                         'name_last': 'fauna'})
    assert response.status_code == 200
    fauna = response.json()

    response = requests.post(f"{BASE_URL}/channels/create/v2",
                                 json = {'token': fauna['token'],
                                         'name': 'fauna_ch',
                                         'is_public': True})
    assert response.status_code == 200
    fauna_ch = response.json()

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': fauna['token'],
                                         'channel_id': fauna_ch['channel_id'],
                                         'length': 60})
    assert response.status_code == 200
    
    response = requests.get(f"{BASE_URL}/standup/active/v1",
                                 params = {'token': fauna['token'],
                                           'channel_id': fauna_ch['channel_id']})
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/standup/active/v1",
                                 params = {'token': data['user']['token'],
                                           'channel_id': data['channel']['channel_id']})

    assert response.status_code == 200


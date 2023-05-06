'''
This test is designated for the standup/send/v1 function
It operates by taking in a valid jwt of a user
A channel id of an existing channel
and a message to be sent during the standup period
data_store will gain a new sub-object under

HTTP TEST for:
standup_send_v1
'''

from src.error import InputError, AccessError
from src.config import url
import pytest
import requests
import time

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

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': 9999,
                                         'message': 'input'})
    assert response.status_code == InputError.code


def test_invalid_msg_length(clear_register_and_reset_http):
    '''
    If a negative length is inputted, InputError should be triggered
    '''
    data = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 60})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': ''})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
    'message': 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula\
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
    adipiscing sem neque sed ipsum. Nam quam nu'})
    assert response.status_code == InputError.code


def test_standup_not_running(clear_register_and_reset_http):
    '''
    If another active standup is already running, InputError should be triggered
    '''
    data = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': data['user']['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': 'this should not be queued'})
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

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': user_new['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': 'this should not be queued'})
    assert response.status_code == AccessError.code


def test_send_within_standup(clear_register_and_reset_http):
    '''
    Tests the normal operating condition of queue sending a message within the standup period
    Calls channel/message to check message
    '''
    data = clear_register_and_reset_http
    
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                                 json = {'email': 'nana.tatsudaki@vtub.er',
                                         'password': 'data_science',
                                         'name_first': 'nana',
                                         'name_last': 'tatsudaki'})
    assert response.status_code == 200
    nana = response.json()
    
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
    
    response = requests.post(f'{BASE_URL}/channel/join/v2',
                             json={'token': nana['token'],
                                   'channel_id': data['channel']['channel_id']})
    assert response.status_code == 200
    
    response = requests.post(f'{BASE_URL}/channel/join/v2',
                             json={'token': fauna['token'],
                                   'channel_id': data['channel']['channel_id']})
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': fauna['token'],
                                         'channel_id': fauna_ch['channel_id'],
                                         'length': 3})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/start/v1",
                                 json = {'token': fauna['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'length': 3})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': nana['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': 'hi!'})
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': fauna['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': 'hii, welcome saplings'})
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': fauna['token'],
                                         'channel_id': fauna_ch['channel_id'],
                                         'message': 'hii, welcome saplings'})
    assert response.status_code == 200
    
    time.sleep(0.1)
    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': nana['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': 'i hope one day i can get accepted by cover!'})
    assert response.status_code == 200
    time.sleep(3)
    response = requests.post(f"{BASE_URL}/standup/send/v1",
                                 json = {'token': fauna['token'],
                                         'channel_id': data['channel']['channel_id'],
                                         'message': 'gambarre!'})
    assert response.status_code == InputError.code

    response = requests.get(f"{BASE_URL}/channel/messages/v2",
                            params={"token": fauna['token'], "channel_id": data['channel']['channel_id'],
                                    "start": 0})
    assert response.status_code == 200
    stdup_msg = response.json()
    assert stdup_msg['messages'][0]['message'] == 'nanatatsudaki: hi!\nceresfauna: hii, welcome saplings\nnanatatsudaki: i hope one day i can get accepted by cover!\n'


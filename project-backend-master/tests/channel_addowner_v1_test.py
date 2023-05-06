''' import for testing channel_addowner function '''
import pytest

from src.error import InputError, AccessError

import requests
from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_user_and_reset_http():
    '''
    This function creates auth and member users
    which are used to test the dm/list function
    '''

    user_all = []
    channel_all = []

    requests.delete(f'{BASE_URL}/clear/v1')
    response = requests.post(f'{BASE_URL}/auth/register/v2',
                             json={'email': 'felix.li@vtub.er',
                                   'password': 'emptied',
                                   'name_first': 'felix',
                                   'name_last': 'li'})
    assert response.status_code == 200
    user_all.append(response.json())

    response = requests.post(f'{BASE_URL}/auth/register/v2',
                             json={'email': 'mako.fuka@vtub.er',
                                   'password': 'passwor',
                                   'name_first': 'mako',
                                   'name_last': 'fuka'})
    assert response.status_code == 200
    user_all.append(response.json())

    response = requests.post(f'{BASE_URL}/auth/register/v2',
                             json={'email': 'homou.nene@vtub.er',
                                   'password': 'ceet2u3',
                                   'name_first': 'homou',
                                   'name_last': 'nene'})
    assert response.status_code == 200
    user_all.append(response.json())

    print(user_all)

    response = requests.post(f'{BASE_URL}/channels/create/v2',
                             json={'token': user_all[0]['token'],
                                   'name': 'rizu_ch',
                                   'is_public': True})
    assert response.status_code == 200
    channel_all.append(response.json())

    response = requests.post(f'{BASE_URL}/channel/join/v2',
                             json={'token': user_all[1]['token'],
                                   'channel_id': channel_all[0]['channel_id']})
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}/channel/join/v2',
                             json={'token': user_all[2]['token'],
                                   'channel_id': channel_all[0]['channel_id']})

    response = requests.post(f'{BASE_URL}/channels/create/v2',
                             json={'token': user_all[1]['token'],
                                   'name': 'mafu_ch',
                                   'is_public': False})
    assert response.status_code == 200
    channel_all.append(response.json())

    response = requests.post(f'{BASE_URL}/channel/invite/v2',
                             json={'token': user_all[1]['token'],
                                   'channel_id': channel_all[1]['channel_id'],
                                   'u_id': user_all[2]['auth_user_id']})

    return user_all, channel_all


def test_addowner_channel_id_invalid(clear_register_user_and_reset_http):
    '''
    Test if an invalid channel_id is provided, it should raise input error
    HTTP test
    '''

    user_all, channel_all = clear_register_user_and_reset_http

    # check channels_all availability
    print(channel_all)

    response = requests.post(f'{BASE_URL}/channel/addowner/v1',
                             json={'token': user_all[0]['token'],
                                   'channel_id': 9999,
                                   'u_id': user_all[1]['auth_user_id']})
    assert response.status_code == InputError.code


def test_addowner_user_id_invalid(clear_register_user_and_reset_http):
    '''
    Test if an invalid u_id is provided, it should raise input error
    HTTP test
    '''
    user_all, channel_all = clear_register_user_and_reset_http

    # check channels_all availability
    print(channel_all)

    response = requests.post(f'{BASE_URL}/channel/addowner/v1',
                             json={'token': user_all[0]['token'],
                                   'channel_id': channel_all[0]['channel_id'],
                                   'u_id': 9999})
    assert response.status_code == InputError.code


def test_addowner_user_not_member(clear_register_user_and_reset_http):
    '''
    Test if a non-member's u_id is provided, it should raise input error
    HTTP test
    '''
    user_all, channel_all = clear_register_user_and_reset_http

    # check channels_all availability
    print(channel_all)

    response = requests.post(f'{BASE_URL}/channel/addowner/v1',
                             json={'token': user_all[1]['token'],
                                   'channel_id': channel_all[1]['channel_id'],
                                   'u_id': user_all[0]['auth_user_id']})
    assert response.status_code == InputError.code


def test_addowner_user_already_owner(clear_register_user_and_reset_http):
    '''
    Test if the u_id's corresponding user is already owner, it should raise input error
    HTTP test
    '''
    user_all, channel_all = clear_register_user_and_reset_http

    # check channels_all availability
    print(channel_all)

    response = requests.post(f'{BASE_URL}/channel/addowner/v1',
                             json={'token': user_all[0]['token'],
                                   'channel_id': channel_all[0]['channel_id'],
                                   'u_id': user_all[0]['auth_user_id']})
    assert response.status_code == InputError.code


def test_addowner_user_not_authorised(clear_register_user_and_reset_http):
    '''
    Test if an unauthorised user is calling this function, it should raise access error
    By non-autorised it means either not an owner of the channel
    Or not a global owner who is a member of the current channel
    HTTP test
    '''
    user_all, channel_all = clear_register_user_and_reset_http
    print(user_all)
    # check channels_all availability
    print(channel_all)

    response = requests.post(f'{BASE_URL}/channel/addowner/v1',
                             json={'token': user_all[2]['token'],
                                   'channel_id': channel_all[0]['channel_id'],
                                   'u_id': user_all[1]['auth_user_id']})
    assert response.status_code == AccessError.code


def test_addowner_global_owner(clear_register_user_and_reset_http):
    '''
    Test if a global owner calls the function as a member,
    The appointed member will be promoted to owner
    HTTP test
    '''
    user_all, channel_all = clear_register_user_and_reset_http
    print(user_all)
    # check channels_all availability
    print(channel_all)

    response = requests.post(f'{BASE_URL}/admin/userpermission/change/v1',
                             json={'token': user_all[0]['token'],
                                   'u_id': user_all[2]['auth_user_id'],
                                   'permission_id': 1})
    assert response.status_code == 200

    response = requests.post(f'{BASE_URL}/channel/addowner/v1',
                             json={'token': user_all[2]['token'],
                                   'channel_id': channel_all[0]['channel_id'],
                                   'u_id': user_all[1]['auth_user_id']})
    assert response.status_code == 200

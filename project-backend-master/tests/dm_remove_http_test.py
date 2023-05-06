''' import for testing dm_create function '''
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
    dm_all = []

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

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_all[0]['token'],
                                   'u_ids': [user_all[1]['auth_user_id'],
                                             user_all[2]['auth_user_id']]})
    assert response.status_code == 200
    dm_all.append(response.json())
    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_all[1]['token'],
                                   'u_ids': [user_all[2]['auth_user_id']]})
    assert response.status_code == 200
    dm_all.append(response.json())

    return user_all, dm_all


def test_remove_invalid_id_http(clear_register_user_and_reset_http):
    '''
    Test if an invalid dm_id is provided
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.delete(f'{BASE_URL}/dm/remove/v1',
                               json={'token': user_all[0]['token'],
                                     'dm_id': 9999})
    assert response.status_code == InputError.code


def test_remove_not_authorised(clear_register_user_and_reset_http):
    '''
    Check if an unauthorised user is calling this function and blocks the action
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.delete(f'{BASE_URL}/dm/remove/v1',
                               json={'token': user_all[2]['token'],
                                     'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == AccessError.code

    response = requests.delete(f'{BASE_URL}/dm/remove/v1',
                               json={'token': user_all[1]['token'],
                                     'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == AccessError.code


def test_remove_owner_left_http(clear_register_user_and_reset_http):
    '''
    Test if former owner can initiate remove option
    The owner must have left the group
    HTTP test
    '''

    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.post(f'{BASE_URL}/dm/leave/v1',
                             json={'token': user_all[0]['token'],
                                   'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == 200

    response = requests.delete(f'{BASE_URL}/dm/remove/v1',
                               json={'token': user_all[0]['token'],
                                     'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == AccessError.code


def test_remove_working_http(clear_register_user_and_reset_http):
    '''
    Test if dm_remove works in normal circumstance
    Removes all users from the DM (including owner)
    Will NOT delete the entry form data_store
    i.e. dm_id is untouched, msg is untouched
    This test can only assess the working state
    HTTP Test
    '''

    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.delete(f'{BASE_URL}/dm/remove/v1',
                               json={'token': user_all[0]['token'],
                                     'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == 200

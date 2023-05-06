''' import for testing dm_create function '''
import pytest

from src.error import InputError

import requests
from src.config import url

BASE_URL = url


@pytest.fixture
def clear_register_user_and_reset_http():
    '''
    This function creates auth and member users
    which are used to test the dm/create function
    '''

    user_all = []

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

    return user_all


def test_dm_create_invalid_http(clear_register_user_and_reset_http):
    '''
    Tests invalid user_id in u_ids list
    HTTP test
    '''
    user_list = clear_register_user_and_reset_http

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_list[0]['token'],
                                   'u_ids': [10]})
    assert response.status_code == InputError.code


def test_dm_create_empty_http(clear_register_user_and_reset_http):
    '''
    Tests owner creating a testing DM, in other word a DM with no other members
    The DM should be created within data_store['dms'] with dm_id 0x1
    HTTP test
    '''
    user_list = clear_register_user_and_reset_http

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_list[0]['token'],
                                   'u_ids': []})
    assert response.status_code == 200
    new_dm_id = response.json()
    assert new_dm_id['dm_id'] == 1


def test_dm_create_dupe_http(clear_register_user_and_reset_http):
    '''
    Tests the response if duplicate user ids are in u_ids list
    HTTP test
    '''
    user_list = clear_register_user_and_reset_http

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_list[0]['token'],
                                   'u_ids': [user_list[1]['auth_user_id'],
                                             user_list[1]['auth_user_id'],
                                             user_list[2]['auth_user_id']]})
    assert response.status_code == InputError.code

# PROBLEM: owner_id can be placed in u_ids list, but will not cause overlap. Fix needed


def test_dm_create_type_http(clear_register_user_and_reset_http):
    '''
    Ensures that the dm_create function returns the correct datatype
    '''

    user_list = clear_register_user_and_reset_http

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_list[0]['token'],
                                   'u_ids': [user_list[1]['auth_user_id'],
                                             user_list[2]['auth_user_id']]})
    response.status_code = 200
    dm_1 = response.json()

    response = requests.post(f'{BASE_URL}/dm/create/v1',
                             json={'token': user_list[1]['token'],
                                   'u_ids': [user_list[2]['auth_user_id']]})
    response.status_code = 200
    dm_2 = response.json()

    assert isinstance(dm_1['dm_id'], int)
    assert isinstance(dm_2['dm_id'], int)

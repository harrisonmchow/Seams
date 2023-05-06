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


def test_details_invalid_id_http(clear_register_user_and_reset_http):
    '''
    Test if an invalid dm_id is provided to the function, it should throw an exception
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': user_all[0]['token'],
                                    'dm_id': 9999})
    assert response.status_code == InputError.code


def test_details_unauthorised_http(clear_register_user_and_reset_http):
    '''
    Test if an user that is not a member calls the function, it should block the action
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.post(f'{BASE_URL}/auth/register/v2',
                             json={'email': 'lu.lu@niji.retired',
                                   'password': 'conlulu',
                                   'name_first': 'lu',
                                   'name_last': 'lu'})

    response = requests.post(f'{BASE_URL}/auth/login/v2',
                             json={'email': 'lu.lu@niji.retired',
                                   'password': 'conlulu'})
    assert response.status_code == 200
    user_all.append(response.json())

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': user_all[3]['token'],
                                    'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == AccessError.code


def test_details_type_http(clear_register_user_and_reset_http):
    '''
    Test if details return the correct datatype
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': user_all[0]['token'],
                                    'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == 200
    test_return = response.json()

    assert isinstance(test_return['name'], str)
    assert isinstance(test_return['members'], list)
    assert isinstance(test_return['members'][0]['u_id'], int)
    assert isinstance(test_return['members'][0]['email'], str)
    assert isinstance(test_return['members'][0]['name_first'], str)
    assert isinstance(test_return['members'][0]['name_last'], str)
    assert isinstance(test_return['members'][0]['handle_str'], str)


def test_details_owner_confirmation(clear_register_user_and_reset_http):
    '''
    Confirms DM owner's presence in the member list in details
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            params={'token': user_all[0]['token'],
                                    'dm_id': dm_all[0]['dm_id']})
    assert response.status_code == 200
    test_return = response.json()

    assert test_return['members'][-1]['u_id'] == 1

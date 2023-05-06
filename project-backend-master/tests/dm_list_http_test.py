''' import for testing dm_create function '''
import pytest

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


def test_dm_list_type_http(clear_register_user_and_reset_http):
    '''
    This function tests output types of dm_list
    Here we are assuming dm_list is a list of dm_ids
    The above return types are not specified in markup
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.get(f'{BASE_URL}/dm/list/v1',
                            params={'token': user_all[2]['token']})
    assert response.status_code == 200
    output = response.json()

    assert isinstance(output['dms'], list)
    assert isinstance(output['dms'][0], dict)
    assert isinstance(output['dms'][0]['dm_id'], int)
    assert isinstance(output['dms'][0]['name'], str)


def test_dm_list_empty_http(clear_register_user_and_reset_http):
    '''
    This function tests if a user that doesn't belong to any dms calls
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

    response = requests.get(f'{BASE_URL}/dm/list/v1',
                            params={'token': user_all[3]['token']})
    assert response.status_code == 200
    output = response.json()

    assert not output['dms']


def test_dm_list_creator(clear_register_user_and_reset_http):
    '''
    This function tests if owner gets dm_list
    owner's u_id is not included in u_ids
    but it should also return it dm_list normally
    HTTP test
    '''
    user_all, dm_all = clear_register_user_and_reset_http

    # check dm_all validity
    print(dm_all)

    response = requests.get(f'{BASE_URL}/dm/list/v1',
                            params={'token': user_all[1]['token']})
    assert response.status_code == 200
    output = response.json()
    print(output)
    assert output['dms'][0]['dm_id'] == dm_all[0]['dm_id']
    assert output['dms'][1]['dm_id'] == dm_all[1]['dm_id']

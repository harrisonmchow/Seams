'''
This test is designated for the search_v1 function
It operates by taking in a valid jwt of a user
and a query string containing the keyword or phrase to be searched
The search will be performed in data_store['messages'] and ['dm_messages']

HTTP TEST for:
search_v1
'''

from src.error import InputError, AccessError
from src.config import url
import pytest
import requests

BASE_URL = url


@pytest.fixture
def clear_register_and_reset_http():
    response = requests.delete(f'{BASE_URL}/clear/v1')
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={'email': 'felix.li@vtub.er',
                                   'password': 'emptied',
                                   'name_first': 'felix',
                                   'name_last': 'li'})
    assert response.status_code == 200
    user = response.json()

    response = requests.post(f"{BASE_URL}/channels/create/v2",
                             json={'token': user['token'],
                                   'name': 'rizu_ch',
                                   'is_public': True})
    assert response.status_code == 200
    channel = response.json()

    return user, channel


def test_string_invalid(clear_register_and_reset_http):
    '''
    This tests the InputError condition of search_v1
    For strings less than 1 or greater than 1000 in length
    '''
    user, channel = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={'token': user['token'],
                                   'channel_id': channel['channel_id'],
                                   'message': 'I will make a live2d AI'})
    assert response.status_code == 200

    invalid_str_1 = ''
    invalid_str_2 = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula\
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
    adipiscing sem neque sed ipsum. Nam quam nu'

    response = requests.get(f'{BASE_URL}/search/v1',
                            params={'token': user['token'],
                                    'query_str': invalid_str_1})
    assert response.status_code == InputError.code
    response = requests.get(f'{BASE_URL}/search/v1',
                            params={'token': user['token'],
                                    'query_str': invalid_str_2})
    assert response.status_code == InputError.code


def test_string_casefold(clear_register_and_reset_http):
    '''
    This tests the case-insensitive property of search_v1
    Testing against the same word of different case status
    '''
    user, channel = clear_register_and_reset_http

    response = requests.post(f"{BASE_URL}/message/send/v1",
                             json={'token': user['token'],
                                   'channel_id': channel['channel_id'],
                                   'message': 'I will make a live2d AI'})
    assert response.status_code == 200
    
    response = requests.post(f"{BASE_URL}/dm/create/v1",
                             json={'token': user['token'],
                                   'u_ids': []})
    assert response.status_code == 200
    dm = response.json()
    
    response = requests.post(f"{BASE_URL}/message/senddm/v1",
                             json={'token': user['token'],
                                   'dm_id': dm['dm_id'],
                                   'message': 'I will make a live2d AI'})
    assert response.status_code == 200

    response = requests.get(f'{BASE_URL}/search/v1',
                            params={'token': user['token'],
                                    'query_str': 'WILL'})
    assert response.status_code == 200
    assert len(response.json()['messages']) == 2
    response = requests.get(f'{BASE_URL}/search/v1',
                            params={'token': user['token'],
                                    'query_str': 'wiLl'})
    assert response.status_code == 200
    assert len(response.json()['messages']) == 2
    response = requests.get(f'{BASE_URL}/search/v1',
                            params={'token': user['token'],
                                    'query_str': 'wi ll'})
    assert response.status_code == 200
    assert len(response.json()['messages']) == 0

# huge dictionary test can be put later to ensure reliabilities

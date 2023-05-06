from src.config import url
import sys
import os
import requests
import json
sys.path.append(os.getcwd())


def clear_v1():
    requests.delete(url + 'clear/v1')


def auth_register_v2(email, password, name_first, name_last):
    return requests.post(url + 'auth/register/v2', json={
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
    }).json()


def channels_create_v2(token, name, is_public):
    return requests.post(url + 'channels/create/v2', json={
        'token': token,
        'name': name,
        'is_public': is_public,
    }).json()


def channels_list_v2(token):
    return requests.get(url + 'channels/list/v2', params={
        'token': token,
    }).json()


def test_clear():
    clear_v1()
    auth_register_v2('email@email.com', 'password', 'first', 'last')
    clear_v1()
    auth_register_v2('email@email.com', 'password', 'first', 'last')


def test_auth_register():
    clear_v1()
    data = auth_register_v2('email@email.com', 'password', 'first', 'last')
    assert isinstance(data, dict) and 'token' in data and isinstance(
        data['token'], str)


def test_channels_create():
    clear_v1()
    token = auth_register_v2(
        'email@email.com', 'password', 'first', 'last')['token']
    data = channels_create_v2(token, 'channel name', True)
    assert isinstance(data, dict) and 'channel_id' in data and isinstance(
        data['channel_id'], int)


def test_channels_list():
    name = 'channel name'
    clear_v1()
    token = auth_register_v2(
        'email@email.com', 'password', 'first', 'last')['token']
    channel_id = channels_create_v2(token, name, True)['channel_id']
    data = channels_list_v2(token)
    assert isinstance(data, dict) and 'channels' in data and len(
        data['channels']) == 1
    assert isinstance(
        data['channels'][0], dict) and 'channel_id' in data['channels'][0] and 'name' in data['channels'][0]
    assert isinstance(data['channels'][0]['channel_id'],
                      int) and data['channels'][0]['channel_id'] == channel_id
    assert isinstance(data['channels'][0]['name'],
                      str) and data['channels'][0]['name'] == name


if __name__ == '__main__':
    tests = [test_clear, test_auth_register,
             test_channels_create, test_channels_list]
    failed = 0
    for f in tests:
        try:
            f()
        except:
            failed += 1
    print(f'You passed {len(tests) - failed} out of {len(tests)} tests.')

import pytest
from src.auth import auth_register_v2
from src.other import clear_v1, encode_token
from src.error import InputError, AccessError
from src.user import user_set_handle

import requests
from src.config import url
BASE_URL = url

# Whitebox setup_____________________________________________


@pytest.fixture
def setup():
    clear_v1()
    user_id1 = auth_register_v2(
        "harry@unsw.edu.au", "Password123", "harry", "chow")
    user_id2 = auth_register_v2(
        "jack@unsw.edu.au", "Comp1531iseasy", "jack", "adams")
    user_id3 = auth_register_v2(
        'email1@gmail.com', 'password1', 'first', 'last')
    user_id4 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')

    return [user_id1['auth_user_id'], user_id2['auth_user_id'], user_id3['auth_user_id'], user_id4['auth_user_id']]

# Blackbox steup____________________________________________


@pytest.fixture
def clear_reg():
    print(f"{BASE_URL}/clear/v1")
    response = requests.delete(f"{BASE_URL}/clear/v1")

    assert response.status_code == 200


@pytest.fixture
def add_u1():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email1@gmail.com", "password": "password1", "name_first": "first", "name_last": "last"})
    assert response.status_code == 200
    return response.json()  # returns token and auth user id


@pytest.fixture
def add_u2():
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json={"email": "email2@gmail.com", "password": "password2", "name_first": "firsttwo", "name_last": "lasttwo"})
    assert response.status_code == 200
    return response.json()  # returns token and auth user id


def add_ch_1(token, name, is_public):
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": token, "name": name, "is_public": is_public})
    assert response.status_code == 200
    return response.json()
# ____________________________________________________________________________________-

# White Box tests


def test_too_short(setup):
    u_id1 = setup[0]

    with pytest.raises(InputError):
        user_set_handle(u_id1, "HC")


def test_too_long(setup):
    u_id1 = setup[0]
    with pytest.raises(InputError):
        user_set_handle(
            u_id1, "iDONTknowHOWlongIcanMAKEthisANDiCANTbeBOTHEREDtoCOUNThowMANYcharactersTHISis")


def test_not_alphanumeric(setup):
    u_id1 = setup[0]
    with pytest.raises(InputError):
        user_set_handle(
            u_id1, "Notvalidstuff??!:_")


def test_duplicate(setup):
    u_id1 = setup[0]
    u_id2 = setup[1]

    user_set_handle(
        u_id1, "Duplicate")
    with pytest.raises(InputError):
        user_set_handle(
            u_id2, "Duplicate")


# __________________________________________________
# http Blackbox tests


def test_http_short(clear_reg, add_u1):

    u1_token = add_u1['token']
    handle_str = "HC"
    response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": u1_token, "handle_str": handle_str})

    assert response.status_code == InputError.code


def test_http_long(clear_reg, add_u1):

    u1_token = add_u1['token']
    handle_str = "iDONTknowHOWlongIcanMAKEthisANDiCANTbeBOTHEREDtoCOUNThowMANYcharactersTHISis"
    response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": u1_token, "handle_str": handle_str})

    assert response.status_code == InputError.code


def test_http_alphanum(clear_reg, add_u1):

    u1_token = add_u1['token']
    handle_str = "Notvalidstuff??!:_"

    response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": u1_token, "handle_str": handle_str})

    assert response.status_code == InputError.code


def test_http_duplicate(clear_reg, add_u1, add_u2):

    u1_token = add_u1['token']
    u2_token = add_u2['token']
    handle_str = "Nickname"
    requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": u1_token, "handle_str": handle_str})
    response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": u2_token, "handle_str": handle_str})

    assert response.status_code == InputError.code


def test_http_invalid_auth(clear_reg, add_u1, add_u2):
    token = encode_token(-1)
    handle_str = "Nickname"
    response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": token, "handle_str": handle_str})
    assert response.status_code == AccessError.code


def test_http_invalid_tok(clear_reg, add_u1, add_u2):
    token = 1
    handle_str = "Nickname"
    response = requests.put(
        f"{BASE_URL}/user/profile/sethandle/v1", json={"token": token, "handle_str": handle_str})
    assert response.status_code == AccessError.code


def test_dm_handle_change(clear_reg, add_u1):
    '''
    Runs the reset handle method, ensures that the handle of user
    in DM has been updated.
    This test is necessary due to how DM stores its members
    HTTP test
    '''
    user = add_u1

    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "kson@vtub.er", "password": "password",
                                   "name_first": "Kson", "name_last": "Onair"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "kson@vtub.er", "password": "password"})
    assert response.status_code == 200
    user_2 = response.json()
    
    response = requests.post(f"{BASE_URL}/auth/register/v2",
                             json={"email": "aloe.x@holo.grad", "password": "password",
                                   "name_first": "aloe", "name_last": "x"})

    response = requests.post(f"{BASE_URL}/auth/login/v2",
                             json={"email": "aloe.x@holo.grad", "password": "password"})
    assert response.status_code == 200
    user_3 = response.json()



    response = requests.post(f'{BASE_URL}/dm/create/v1',
                    json = {'token': user['token'],
                    'u_ids': [user_3['auth_user_id'], user_2['auth_user_id']]})
    assert response.status_code == 200
    dm_info = response.json()

    response = requests.put(
        f'{BASE_URL}/user/profile/sethandle/v1',
                    json = {'token': user['token'],
                    'handle_str': 'felixli'})

    response = requests.put(
        f'{BASE_URL}/user/profile/sethandle/v1',
                    json = {'token': user_2['token'],
                    'handle_str': 'ksononair'})

    response = requests.put(
        f'{BASE_URL}/user/profile/sethandle/v1',
                    json = {'token': user_3['token'],
                    'handle_str': 'manoaloe'})
    
    response = requests.get(f'{BASE_URL}/dm/details/v1',
                            {'token': user['token'],
                             'dm_id': dm_info['dm_id']})
    assert response.status_code == 200
    output = response.json()
    assert output['members'][-1]['handle_str'] == 'felixli'
    assert output['members'][0]['handle_str'] == 'manoaloe'
    assert output['members'][1]['handle_str'] == 'ksononair'
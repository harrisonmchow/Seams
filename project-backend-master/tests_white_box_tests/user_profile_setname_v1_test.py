'''
This test fle was used to validate the functionality of the user_profile_setname_v1
function using white box tests via pytest.

Functions:
    test_first_name_too_long()
    test_first_name_too_short()
    test_last_name_too_long()
    test_last_name_too_short()
'''
import pytest
import requests
from src.error import InputError
from src.config import url
from src.other import clear_v1
from src.auth import auth_register_v2
from src.user import user_profile_setname_v1

BASE_URL = url


def test_name_first_too_short():
    '''
    Test first name too short
    '''
    clear_v1()
    user = auth_register_v2('john.smith@unsw.edu.au',
                            'password', 'John', 'Smith')
    with pytest.raises(InputError):
        user_profile_setname_v1(user['auth_user_id'], "", "Smith")


def test_name_last_too_short():
    '''
    Test last name too short
    '''
    clear_v1()
    user = auth_register_v2('john.smith@unsw.edu.au',
                            'password', 'John', 'Smith')
    with pytest.raises(InputError):
        user_profile_setname_v1(user['auth_user_id'], "John", "")


def test_name_first_too_long():
    '''
    Test first name too long
    '''
    clear_v1()
    user = auth_register_v2('john.smith@unsw.edu.au',
                            'password', 'John', 'Smith')
    with pytest.raises(InputError):
        user_profile_setname_v1(
            user['auth_user_id'], "AF1L6NqMIpEjiAvyUGxso4RkDcJOx5hVl6Jonl0zF453OaCGT9b", "Smith")


def test_name_last_too_long():
    '''
    Test last name too long
    '''
    clear_v1()
    user = auth_register_v2('john.smith@unsw.edu.au',
                            'password', 'John', 'Smith')
    with pytest.raises(InputError):
        user_profile_setname_v1(
            user['auth_user_id'], "John", "AF1L6NqMIpEjiAvyUGxso4RkDcJOx5hVl6Jonl0zF453OaCGT9b")

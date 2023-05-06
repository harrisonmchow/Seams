'''
docstring
'''
import pytest
from src.auth import auth_login_v2, auth_register_v2, create_token
from src.error import AccessError
from src.verify_session import verify_session
from src.other import clear_v1

''''
def test_user_not_authorised():  # not logged in
    

    clear_v1()
    return_value = auth_register_v2('gerard.mathews@unsw.edu.au',
                                    'password', 'gerard', 'mathews')
    with pytest.raises(AccessError):
        verify_session(return_value['token'])
'''


def test_user_not_registered():  # not_registered (deleted user)
    '''
    wef
    '''
    clear_v1()
    return_value = create_token(420)
    with pytest.raises(AccessError):
        verify_session(return_value)


def test_invalid_jwt():
    '''
    wef
    '''

    clear_v1()
    with pytest.raises(AccessError):
        verify_session("weoiferiufgnbwlieurgjn")


def test_valid_session():
    '''
    owefown
    '''
    clear_v1()
    auth_register_v2('gerard.mathews@unsw.edu.au',
                     'password', 'gerard', 'mathews')
    return_value = auth_login_v2('gerard.mathews@unsw.edu.au', 'password')
    assert verify_session(
        return_value['token']) == return_value['auth_user_id']

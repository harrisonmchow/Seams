'''
This test fle aims to validate the functionality of the channel_join_v1
function using pytest.

Functions:
    test_invalid_ch_id()
    test_user_joined()
    test_private()
'''
import pytest
from src.auth import auth_register_v2
from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1


def test_invalid_ch_id():
    '''
    Testing an invalid channel id
    '''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')

    channels_create_v1(reg1['auth_user_id'], 'test_channel', True)
    with pytest.raises(InputError):
        channel_join_v1(reg2['auth_user_id'], 2)


def test_user_joined():
    ''' Testing if the user already joined'''
    clear_v1()

    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')

    channels_create_v1(reg1['auth_user_id'], 'test_channel', True)
    channel_join_v1(reg2['auth_user_id'], 1)
    with pytest.raises(InputError):
        channel_join_v1(reg2['auth_user_id'], 1)


def test_private():
    ''' Testing if the channel is private and the user is not authorised'''
    clear_v1()

    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')
    channels_create_v1(reg1['auth_user_id'], 'test_channel', False)
    with pytest.raises(AccessError):
        channel_join_v1(reg2['auth_user_id'], 1)


'''
def test_invalid_token():
    # Iteration 1 tesing
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    ch_id = channels_create_v1(reg1['auth_user_id'], 'test_channel', False)
    with pytest.raises(AccessError):
        channel_join_v1(-1, ch_id['channel_id'])
'''
# it 1


def test_global_join():
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'a', 'b')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'j', 'p')
    ch_id = channels_create_v1(
        reg2['auth_user_id'], 'Test_channel', False)  # private made by 2
    channel_join_v1(reg1['auth_user_id'], ch_id['channel_id'])

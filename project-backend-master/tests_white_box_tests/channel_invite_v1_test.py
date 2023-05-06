'''
This test fle aims to validate the functionality of the channel_invite_v1
function using pytest.

Functions:
    test_invalid_ch_id()
    test_no_ch()
    test_invalid_user_id()
    test_user_is_member()
    test_not_authorised()
'''
import pytest
from src.auth import auth_register_v2
from src.channel import channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1


def test_invalid_ch_id():
    ''' Testing an invalid channel id'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')

    channels_create_v1(reg1['auth_user_id'], 'test_channel', True)

    with pytest.raises(InputError):
        channel_invite_v1(reg1['auth_user_id'], 2, reg2['auth_user_id'])


def test_no_ch():
    '''Testing if there is no channels at all'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')
    with pytest.raises(InputError):
        channel_invite_v1(reg1['auth_user_id'], 2, reg2['auth_user_id'])


def test_invalid_user_id():
    '''Testing an invalid user id'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    ch_id = channels_create_v1(reg1['auth_user_id'], 'test_channel', True)

    with pytest.raises(InputError):
        channel_invite_v1(reg1['auth_user_id'], ch_id['channel_id'], 3)


def test_user_is_member():
    '''Testing if the user is already a member'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')
    ch_id = channels_create_v1(reg1['auth_user_id'], 'test_channel', True)
    channel_join_v1(reg2['auth_user_id'], ch_id['channel_id'])

    with pytest.raises(InputError):
        channel_invite_v1(reg1['auth_user_id'],
                          ch_id['channel_id'], reg2['auth_user_id'])


def test_not_authorised():
    '''Checking if the inviter is authorised'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')
    reg3 = auth_register_v2(
        'email3@gmail.com', 'password3', 'firstthree', 'lastthree')

    ch_id = channels_create_v1(reg1['auth_user_id'], 'test_channel', False)
    with pytest.raises(AccessError):
        channel_invite_v1(reg2['auth_user_id'],
                          ch_id['channel_id'], reg3['auth_user_id'])

# iteration 1


'''
def test_invalid_token():
    #woodys_public_toybox = channels_create_v1(name='woodys toybox', is_public=True, channel_id=1, owner_members=[1], all_members=[])

    # user_buzz = User(email='buzz.lightyear@starcommand.com', password='qazwsx@@',
    #                 name_first='buzz', name_last='lightyear', u_id=2, token=2)
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')
    ch_id = channels_create_v1(reg1['auth_user_id'], 'channel', True)
    with pytest.raises(AccessError):
        channel_invite_v1(-1, ch_id['channel_id'], reg2['auth_user_id'])
'''

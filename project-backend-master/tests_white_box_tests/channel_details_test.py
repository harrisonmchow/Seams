'''
Testing the channel detials implementation

This test fle aims to validate the functionality of the channel_details_v1
function using pytest.

Functions:
    test_no_ch()
    test_invalid_index()
    test_not_authorised()
    test_output_type()
    test_output_correct()
'''
import pytest
from src.auth import auth_register_v2
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1
import requests
from src.config import url
BASE_URL = url


def test_no_ch():
    '''Testing an invalid channel that doesnt exist with user existing'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    with pytest.raises(InputError):
        channel_details_v1(reg1['auth_user_id'], 1)


def test_invalid_index():
    ''' Testing invalid channel for a channel out of the index'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    channels_create_v1(reg1['auth_user_id'], 'test-channel', True)
    with pytest.raises(InputError):
        channel_details_v1(1, 3)


def test_not_authorised():
    '''Testing when the channel ID is valid, but user
    is not a member of the channel'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1',
                            'first', 'last')['auth_user_id']
    reg2 = auth_register_v2('email2@gmail.com', 'password1',
                            'first', 'last')['auth_user_id']
    channels_create_v1(reg1, 'Test_channel', False)
    with pytest.raises(AccessError):
        channel_details_v1(reg2, 1)


def test_output_type():
    ''' Testing the output type as per the spec'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'first', 'last')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'firsttwo', 'lasttwo')
    ch_id = channels_create_v1(reg1['auth_user_id'], 'Test_channel', True)
    channel_join_v1(reg2['auth_user_id'], ch_id['channel_id'])

    out = channel_details_v1(1, 1)

    assert isinstance(out, dict) is True
    assert isinstance(out['name'], str) is True
    assert isinstance(out['is_public'], bool) is True
    assert isinstance(out['owner_members'], list) is True
    assert isinstance(out['all_members'], list) is True
    assert isinstance(out['owner_members'][0], dict) is True
    assert isinstance(out['all_members'][0], dict) is True
    assert isinstance(out['all_members'][1], dict) is True


def test_output_correct():
    '''Testing that the output is correct as per spec'''
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1', 'a', 'b')
    reg2 = auth_register_v2(
        'email2@gmail.com', 'password2', 'j', 'p')
    ch_id = channels_create_v1(reg1['auth_user_id'], 'Test_channel', True)
    channel_invite_v1(reg1['auth_user_id'],
                      ch_id['channel_id'], reg2['auth_user_id'])

    out = channel_details_v1(reg1['auth_user_id'], 1)
    assert out == {
        'name': 'Test_channel',
        'is_public': True,
        'owner_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'a',
          'name_last': 'b',
          'handle_str': 'ab',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}],
        'all_members':
        [{'u_id': 1,
          'email': 'email1@gmail.com',
          'name_first': 'a',
          'name_last': 'b',
          'handle_str': 'ab',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'},
         {'u_id': 2,
         'email': 'email2@gmail.com',
          'name_first': 'j',
          'name_last': 'p',
          'handle_str': 'jp',
          'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}

    # It1 fixes


'''
def test_invalid_auth():
     Testing invalid channel for a channel out of the index
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1',
                            'first', 'last')['auth_user_id']
    channels_create_v1(reg1, 'test-channel', True)
    with pytest.raises(AccessError):
        channel_details_v1(2, 1)

'''
'''def test_invalid_auth2():
     Testing invalid channel for a channel out of the index
    clear_v1()
    reg1 = auth_register_v2('email1@gmail.com', 'password1',
                            'first', 'last')['auth_user_id']
    channels_create_v1(reg1, 'test-channel', True)
    with pytest.raises(AccessError):
        channel_details_v1(-1, 1)'''


# def test_global_details():
#     clear_v1()
#     reg1 = auth_register_v2('email1@gmail.com', 'password1', 'a', 'b')
#     reg2 = auth_register_v2(
#         'email2@gmail.com', 'password2', 'j', 'p')
#     ch_id = channels_create_v1(
#         reg2['auth_user_id'], 'Test_channel', False)  # private made by 2
#     out = channel_details_v1(reg1['auth_user_id'], ch_id['channel_id'])

#     assert out == {
#         'name': 'Test_channel',
#         'is_public': False,
#         'owner_members':
#         [{'u_id': 2,
#          'email': 'email2@gmail.com',
#           'name_first': 'j',
#           'name_last': 'p',
#           'handle_str': 'jp',
#           'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}],
#         'all_members':
#         [{'u_id': 2,
#          'email': 'email2@gmail.com',
#           'name_first': 'j',
#           'name_last': 'p',
#           'handle_str': 'jp',
#           'profile_img_url': 'http://localhost:8080//imgurl/0.jpg'}]}

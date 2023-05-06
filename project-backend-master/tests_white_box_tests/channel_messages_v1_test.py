'''
This test fle aims to validate the functionality of the channel_messages_v1
function using pytest.

These tests are White Box tests.

Functions:
    clear_register_user_and_create_channel()
    test_nonexistent_channel_id()
    test_start_greater_than_message_total()
    test_user_not_member_of_channel()
    test_valid_input()
    test_correct_return_type()
'''
import pytest
from src.auth import auth_register_v2
from src.channel import channel_messages_v1
from src.channels import channels_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def clear_register_user_and_create_channel():
    '''
    This function creates a new user and channel
    which are used to test the channel_messages function
    '''
    clear_v1()                                                  # Clear data
    user = auth_register_v2('john.smith@unsw.edu.au',
                            'password', 'John', 'Smith')               # Create user
    channel = channels_create_v1(
        1, 'Badger Channel', True)     # Create channel
    return user, channel


def test_nonexistent_channel_id():
    '''
    Invalid Channel --> Channel ID doesn't exist. This test should fail
    '''
    clear_v1()
    user = auth_register_v2('john.smith@unsw.edu.au',
                            'password', 'John', 'Smith')

    with pytest.raises(InputError):
        channel_messages_v1(user['auth_user_id'], 5, 0)


def test_start_greater_than_message_total(clear_register_user_and_create_channel):
    '''
    Invalid Start --> Start greater than total number of messages. This test should fail
    '''
    user, channel = clear_register_user_and_create_channel

    with pytest.raises(InputError):
        channel_messages_v1(user['auth_user_id'], channel['channel_id'], 5)


def test_user_not_member_of_channel(clear_register_user_and_create_channel):
    '''
    User not member --> Attempt to view messages from channel
    which user is not apart of. This test should fail
    '''
    channel = clear_register_user_and_create_channel[1]

    with pytest.raises(AccessError):
        channel_messages_v1(5, channel['channel_id'], 0)


def test_valid_input(clear_register_user_and_create_channel):
    '''
    Test Valid Input
    '''
    user, channel = clear_register_user_and_create_channel
    output = channel_messages_v1(
        user['auth_user_id'], channel['channel_id'], 0)
    empty = []
    assert output['messages'] == empty
    assert output['start'] == 0
    assert output['end'] == -1


def test_correct_return_type(clear_register_user_and_create_channel):
    '''
    Verifies that channel_messages returns the correct variable type
    '''
    user, channel = clear_register_user_and_create_channel
    output = channel_messages_v1(
        user['auth_user_id'], channel['channel_id'], 0)

    assert isinstance(output['messages'], list)
    assert isinstance(output['start'], int)
    assert isinstance(output['end'], int)

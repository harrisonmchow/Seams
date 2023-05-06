'''
standup.py:

This script allows a channel member to search all messages in history based on a query.
Data_Store is accessed and search is applied on all messages

Functions:
    standup_running(channel_id, data)
    standup_start_v1(token, channel_id, length)
    standup_active_v1(token, channel_id)
    standup_send_v1(token, channel_id, message)
'''
from src.data_store import data_store, SDUP_INIUSER_ID, SDUP_CH_ID, SDUP_T_END_ID, SDUP_MSGS_ID, CH_MEMBER_IDX
from src.error import InputError, AccessError
from src.verify_session import verify_session
from src.other import check_channel_id
from src.message import message_sendlater_v1
from datetime import datetime


def standup_running(channel_id, data):
    '''
    This is a helper function to check if a standup is running
    Component function of all standup functions

    Arguments:
        channel_id (int) - A channel_id of a valid channel

    Exceptions:
        InputError  - Occurs when ch_id is not valid

    Return Value:
        Return {running_status} (dict | bool)
    '''
    running_status = False

    for ch_sdup in data['standups']:
        curr_time = int(datetime.timestamp(datetime.now()))
        if ch_sdup[SDUP_CH_ID] == channel_id and curr_time < ch_sdup[SDUP_T_END_ID]:
            running_status = True

    return {
        'running_status': running_status,
    }


def standup_start_v1(token, channel_id, length):
    '''
    This function takes in a token of an existing Seams user
    An id of an existing Seams channel
    And the duration which the standup is designated to run for
    If standup is successfully started, it will return the time when it finishes

    Arguments:
        token (str) - A JWT which identifies a user
        channel_id (int) - A channel_id of a valid channel
        length (int) - The length of the standup period

    Exceptions:
        InputError  - Occurs when ch_id is not valid
                    - Occurs when length is negative
                    - Occurs when an active standup is already running

        AccessError - Occurs when ch_id is valid but user is not a member
                    - Occurs when session is invalid (verify_session fails)

    Return Value:
        Returns {time_finish} (dict | int)
    '''
    data = data_store.get()

    curr_channel = check_channel_id(channel_id)
    initiator_id = verify_session(token)
    time_finish = int(datetime.timestamp(datetime.now()))

    if length < 0:
        raise InputError('Standup duration cannot be negative')

    if initiator_id not in curr_channel[CH_MEMBER_IDX]:
        raise AccessError('User is not a member of this channel')

    # standup status checker
    if standup_running(channel_id, data)['running_status'] == True:
        raise InputError('A standup is currently running in this channel')

    new_msg_id = message_sendlater_v1(token, channel_id,
                                      f'placeholder_{initiator_id}', time_finish)

    for later_msg in data['messages_later']:
        if later_msg['channel'] == True and \
           later_msg['location_id'] == channel_id:
            later_msg['message_data']['message'] = ''
            data_store.set(data)

    time_finish += length
    data['standups'].insert(0,
                            [initiator_id, channel_id, time_finish, new_msg_id])

    data_store.set(data)

    return {
        'time_finish': time_finish,
    }


def standup_active_v1(token, channel_id):
    '''
    This function takes in a token of an existing Seams user
    An id of an existing Seams channel
    It will return the status of the current channel standup
    If a standup is running, it will return the time when it ends
    If not, it will return `None`

    Arguments:
        token (str) - A JWT which identifies a user
        channel_id (int) - A channel_id of a valid channel

    Exceptions:
        InputError  - Occurs when ch_id is not valid

        AccessError - Occurs when ch_id is valid but user is not a member
                    - Occurs when session is invalid (verify_session fails)

    Return Value:
        Returns {time_finish} (dict | int)
    '''
    data = data_store.get()

    curr_channel = check_channel_id(channel_id)
    initiator_id = verify_session(token)
    time_finish = None

    if standup_running(channel_id, data)['running_status'] == False:
        return {'time_finish': time_finish, }

    if initiator_id not in curr_channel[CH_MEMBER_IDX]:
        raise AccessError('User is not a member of this channel')

    for standup in data['standups']:
        if standup[SDUP_CH_ID] == channel_id:
            time_finish = standup[SDUP_T_END_ID]

    return {
        'time_finish': time_finish,
    }


def standup_send_v1(token, channel_id, message):
    '''
    This function takes in a token of an existing Seams user
    An id of an existing Seams channel
    And the message to be sent during the standup
    It will send a message to the standup buffer of this channel
    If a standup is running, the buffer will be packaged at the end of the standup
    And will be sent as one single message by the initiator of the standup
    If not, it will return `None`

    Arguments:
        token (str) - A JWT which identifies a user
        channel_id (int) - A channel_id of a valid channel
        message (str) - A string of message

    Exceptions:
        InputError  - Occurs when ch_id is not valid
                    - Occurs when message is over 1000 characters in length
                    - Occurs when no active standup is running

        AccessError - Occurs when ch_id is valid but user is not a member
                    - Occurs when session is invalid (verify_session fails)

    Return Value:
        Returns {}
    '''
    data = data_store.get()

    curr_channel = check_channel_id(channel_id)
    initiator_id = verify_session(token)

    if len(message) > 1000:
        raise InputError('Message cannot be over 1000 characters in length')

    if standup_running(channel_id, data)['running_status'] == False:
        raise InputError('No active standup is running in this channel')

    if initiator_id not in curr_channel[CH_MEMBER_IDX]:
        raise AccessError('User is not a member of this channel')

    new_msg = ''
    for standup in data['standups']:
        if standup[SDUP_CH_ID] == channel_id:
            new_msg += (data['users'][initiator_id - 1]
                        [5] + ': ' + message + '\n')

    for later_msg in data['messages_later']:
        if later_msg['channel'] == True and \
           later_msg['location_id'] == channel_id:
            later_msg['message_data']['message'] += new_msg

    data_store.set(data)
    return {}

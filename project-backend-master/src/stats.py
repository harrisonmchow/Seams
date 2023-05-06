'''
stats.py:

This file contains functions relating to the stats
functionality of the system.

Functions:
    update_ch_stats(auth_user_id, joining)
    update_dm_stats(auth_user_id, joining)
    update_msgs_stats(auth_user_id, time)
    update_workplace_ch_stats()
    update_workplace_dm_stats(creating)
    update_workplace_msg_stats(sending, num)
'''

from src.data_store import data_store
from datetime import datetime


def update_ch_stats(auth_user_id, joining):
    '''
    Description: 'update_ch_stats' is a helper function that updates the datastore whenever a user joins/leaves a channel.
        It helps keep track of the users involvement, which is needed for user/stats/v1.

    Arguments:
        'auth_user_id'  - (int) - An int of the user's id.
        'joining'       - (boolean) - Whether the user is joining or leaving a channel

    Exceptions:
        Null

    Returns:
        Returns {}
    '''
    if joining is True:
        i = 1
    else:
        i = -1
    store = data_store.get()
    for user in store['channel_track']:
        if user['auth_user_id'] == auth_user_id:
            most_recent = user['channels_joined'][-1]
            new_num_ch = most_recent['num_channels_joined'] + i
            time_now = int(datetime.timestamp(datetime.now()))
            new_dict = {
                'num_channels_joined': new_num_ch,
                'time_stamp': time_now,
            }
            user['channels_joined'].append(new_dict)
            # break

    data_store.set(store)
    return {}


def update_dm_stats(auth_user_id, joining):
    '''
    Description: 'update_dm_stats' is a helper function that updates the datastore whenever a user joins/leaves a dm.
        It helps keep track of the users involvement, which is needed for user/stats/v1.

    Arguments:
        'auth_user_id'  - (int) - An int of the user's id.
        'joining'       - (boolean) - Whether the user is joining or leaving a channel

    Exceptions:
        Null

    Returns:
        Returns {}
    '''
    if joining is True:
        i = 1
    else:
        i = -1
    store = data_store.get()
    for user in store['dm_track']:
        if user['auth_user_id'] == auth_user_id:
            most_recent = user['dms_joined'][-1]
            new_num_ch = most_recent['num_dms_joined'] + i
            time_now = int(datetime.timestamp(datetime.now()))
            new_dict = {
                'num_dms_joined': new_num_ch,
                'time_stamp': time_now,
            }
            user['dms_joined'].append(new_dict)
            # break

    data_store.set(store)
    return {}


def update_msgs_stats(auth_user_id, time):
    '''
    Description: 'update_msgs_stats' is a helper function that updates the datastore whenever a user sends a message.
        It helps keep track of the users involvement, which is needed for user/stats/v1.

    Arguments:
        'auth_user_id'  - (int) - An int of the user's id.
        'time'          - (int) - A timestamp of when the message was sent.

    Exceptions:
        Null

    Returns:
        Returns {}
    '''
    store = data_store.get()
    for user in store['message_track']:
        if user['auth_user_id'] == auth_user_id:
            most_recent = user['messages_sent'][-1]
            new_num_ch = most_recent['num_messages_sent'] + 1
            new_dict = {
                'num_messages_sent': new_num_ch,
                'time_stamp': time,
            }
            user['messages_sent'].append(new_dict)
            # break

    data_store.set(store)
    return {}


def update_workplace_ch_stats():
    store = data_store.get()
    most_recent = store['channels_exist'][-1]
    new_num_ch = most_recent['num_channels_exist'] + 1
    now = int(datetime.timestamp(datetime.now()))
    new_ch = {
        'num_channels_exist': new_num_ch,
        'time_stamp': now
    }
    store['channels_exist'].append(new_ch)
    data_store.set(store)
    return {}


def update_workplace_dm_stats(creating):
    if creating is True:
        i = 1
    else:
        i = -1

    store = data_store.get()
    most_recent = store['dms_exist'][-1]
    new_num_dm = most_recent['num_dms_exist'] + i
    now = int(datetime.timestamp(datetime.now()))
    new_dm = {
        'num_dms_exist': new_num_dm,
        'time_stamp': now
    }
    store['dms_exist'].append(new_dm)
    data_store.set(store)
    return {}


def update_workplace_msg_stats(sending, num):

    if sending is True:
        i = 1
    else:
        i = -1

    store = data_store.get()
    most_recent = store['messages_exist'][-1]
    new_num_msg = most_recent['num_messages_exist'] + i*num
    now = int(datetime.timestamp(datetime.now()))
    new_msg = {
        'num_messages_exist': new_num_msg,
        'time_stamp': now
    }
    store['messages_exist'].append(new_msg)
    data_store.set(store)
    return {}

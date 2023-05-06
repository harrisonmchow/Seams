'''
channels.py:

This script contains functions which allow users to view lists of channel
members, channel owerns and to create new channels.

Functions:
    channels_list_v1(auth_user_id)
    channels_listall_v1(auth_user_id)
    channels_create_v1(auth_user_id, name, is_public)
'''
from src.data_store import CH_ID_IDX, CH_MEMBER_IDX, CH_NAME_IDX, data_store
from src.error import InputError
from datetime import datetime
from src.stats import update_ch_stats, update_workplace_ch_stats


def channels_list_v1(auth_user_id):
    '''
    Take in an authenticated user id, and return all channels and their details
    that the user is a member in.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user

    Exceptions: 
        AccessError - Occurs when auth_user_id is not a valid user id.

    Return value:
        channels (list)
    '''

    store = data_store.get()
    all_channels = []
    CH_ID_IDX
    CH_MEMBER_IDX
    CH_NAME_IDX

    # Go through all the channels, and check if the user is in the members list
    # If they are, add it to the all_channels list

    for channel in store['channels']:
        for user_id in channel[CH_MEMBER_IDX]:
            if user_id == auth_user_id:
                all_channels.append(
                    {'channel_id': channel[CH_ID_IDX], 'name': channel[CH_NAME_IDX]})

    return {

        'channels': all_channels

    }


def channels_listall_v1(auth_user_id):
    '''
    Take in an authenticated user id, and return all public/private channels and their details.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user

    Exceptions: 
        AccessError - Occurs when auth_user_id is not a valid user id.

    Returns : channels(list)
    '''
    store = data_store.get()
    all_channels = []
    CH_ID_IDX
    CH_NAME_IDX

    # Go through every channel and return the necessary details

    for channel in store['channels']:
        all_channels.append(
            {'channel_id': channel[CH_ID_IDX], 'name': channel[CH_NAME_IDX]})

    return {

        'channels': all_channels

    }


def channels_create_v1(auth_user_id, name, is_public):
    '''
    Take in an authenticated user id, a channel name, and a boolean indicating whether the channel
    should be public, and create a channel, returning its channel id. Only create the channel
    if the name is of valid length (between 1 and 20 characters inclusive).
    Generate the channel_id based on the number of existing channels.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        name (str) - The name of the channel
        is_public (bool) - A True of False where True is public

    Exceptions:
        InputError - Occurs when the channel name is 0 characters or greater than 20 characters
        AccessError - Occurs when auth_user_id is not a valid user id.

    Return value:
        channel_id (int)
    '''

    store = data_store.get()

    # Check if the name of the channel is valid
    if len(name) == 0 or len(name) > 20:
        raise InputError(description="Invalid name: Channel name cannot be less than 1 \
            character or greater than 20 characters")

    new_channel_id = len(store['channels']) + 1

    # Add the creator of the channel to the list of owners and members
    owner_list = [auth_user_id]
    member_list = [auth_user_id]
    store['channels'].append(
        [new_channel_id, name, is_public, owner_list, member_list])
    store['messages'].append([])
    store['wordle_ch'].append({})
    # Keep track of the user's channels
    data_store.set(store)
    update_ch_stats(auth_user_id, True)
    update_workplace_ch_stats()

    return {
        'channel_id': new_channel_id,
    }

'''
other.py:

This file contains helper functions which are called
in various other functions throughout the system.

Functions:
    clear_v1()
    check_auth_user(auth_user_id)
    check_channel_id(channel_id)
    check_dm_id(dm_id)
    encode_token(auth_id)
'''

from flask import Flask, request, Response
from json import dumps
import jwt
from src.data_store import U_ID_IDX, DM_ID_IDX, data_store
from src.error import AccessError, InputError
import jwt
SECRET = "BADGER"
APP = Flask(__name__)


def clear_v1():
    '''
    This functions clears and resets the data store to it's initial objects.

    Return Value:
        Returns {}
    '''
    #store = data_store.get()
    store = {}
    store['users'] = []
    store['channels'] = []
    store['standups'] = []
    store['messages'] = [[]]
    store['dm_messages'] = [[]]
    store['dms'] = []
    store['message_counter'] = 0
    store['register_counter'] = 0
    store['global_owner'] = []
    store['removed_users'] = []
    store['removed_emails'] = []
    store['removed_handles'] = []
    store['sessions'] = []
    store['messages_later'] = []
    store['channel_track'] = []
    store['dm_track'] = []
    store['message_track'] = []
    store['channels_exist'] = []
    store['dms_exist'] = []
    store['messages_exist'] = []
    store['valid_reacts'] = [1]
    store['wordle_ch'] = [[]]
    store['wordle_dm'] = [[]]

    data_store.set(store)
    return {}


def check_auth_user(auth_user_id):
    '''
    This functions checks that a user id is valid.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user

    Return Value:
        Returns authid_exists (bool) - A value which asserts whether
                                         a user id is valid or not
    '''
    # Checking if auth_user is valid id
    id_idx = 0
    store = data_store.get()
    authid_exists = False
    for user in store['users']:
        if user[id_idx] == auth_user_id:
            authid_exists = True
            break
    return authid_exists


def check_channel_id(channel_id):
    '''
    This functions checks if a channel id is valid
    and returns the channel.

    Arguments:
        channel_id (int) - A uniqe channel id which identifies each channel

    Return Value:
        Returns a list containing information about a channel (ch_id, name_ch,
             public/private, owner members, all members)
    '''

    store = data_store.get()
    # Channel id not existing (assuming it is given as an int)
    print(store['channels'])

    channel_id = int(channel_id)
    ch_exists = False
    find_channel = False
    for idx, ch_get in enumerate(store['channels']):
        if ch_get[U_ID_IDX] == channel_id:
            ch_exists = True
            find_channel = idx
            break
    if ch_exists is False:
        raise InputError(description="Incorrect channel_id")

    return store['channels'][find_channel]


def check_dm_id(dm_id):
    '''
    This functions checks if a dm id is valid
    and returns the dm.

    Arguments:
        dm_id (int) - A uniqe dm id which identifies each dm

    Return Value:
        Returns a list containing information about a dm (dm_id (int),
             owner (dict), members (list), name (str), msg (list of dict))
    '''
    store = data_store.get()
    # Dm id not existing (assuming it is given as an int)
    dm_exists = False
    find_dm = False
    for idx, dm_get in enumerate(store['dms']):
        if dm_get[DM_ID_IDX] == dm_id:
            dm_exists = True
            find_dm = idx
            break
    if dm_exists is False:
        raise InputError(description="Incorrect dm_id")

    return store['dms'][find_dm]


def encode_token(auth_id):
    '''
    This functions encodes a token

    Arguments:
        auth_user_id (int) - A unique id which identifies each user

    Return Value:
        Returns an encoded token.
    '''
    return jwt.encode({"auth_user_id": auth_id}, SECRET, algorithm="HS256")

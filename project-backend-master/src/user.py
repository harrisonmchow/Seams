
'''
user.py:

This files contains functions which allow a user to
edit their profile.

Functions:
    upload_pic(token, img_url, x_start, y_start, x_end, y_end)
    remove_user_v1(auth_user_id, u_id)
    user_set_handle(auth_user_id, handle_str)
    change_userpermission(auth_user_id, u_id, permission_id)
    user_profile_setname_v1(auth_user_id, name_first, name_last)
    user_profile_setemail_v1(auth_user_id, email)
    user_profile_v1(user_id, token)
    user_stats_v1(token)
'''
import jwt
import sys
from src.message import check_message_send_later
from datetime import datetime
from src import auth
from src.config import url
from unicodedata import name
from signal import SIG_DFL
import re
from src.verify_session import verify_session
from src.other import SECRET, check_channel_id, clear_v1
from urllib import request as im_request
import certifi
from PIL import Image
from src.error import AccessError
from src.error import InputError
from src.data_store import CH_MEMBER_IDX, CH_OWN_IDX, DM_MEMBERS_IDX, \
    DM_OWN_IDX, U_EMAIL_IDX, U_HANDLE_IDX, U_ID_IDX, U_NAME_FIRST_IDX, \
    U_NAME_LAST_IDX, U_PFP_IDX, data_store
from flask import request
from jwt import decode
import requests
BASE_URL = url


def upload_pic(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
     Please note: the URL needs to be a non-https URL (it should just have 
     "http://" in the URL. We will only test with non-https URLs.
    Input:
        token(str), 
        img_url(str),
        x_start(int), 
        y_start(int), 
        x_end(int), 
        y_end(int)
    Return:
        NIL - {}

    InputError when :
        - img_url returns an HTTP status other than 200, or any other errors occur when attempting to retrieve the image
        - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
        - x_end is less than or equal to x_start or y_end is less than or equal to y_start
        - image uploaded is not a JPG
    '''
    store = data_store.get()
    auth_user_id = verify_session(token)
    # Checking cases
    try:
        requests.get(img_url)
    except:
        raise InputError(description="Not a valid url") from InputError

    im_request.urlretrieve(img_url, f"./src/pfps/file")
    try:
        img = Image.open(f"./src/pfps/file")
    except:
        raise InputError(description="Not an image url") from InputError

    if img.format != "JPEG":
        raise InputError(description="Not a JPG")
    # Saving image as <auth_user_id>.jpg
    im_request.urlretrieve(img_url, f"./src/pfps/{auth_user_id}.jpg")
    img = Image.open(f"./src/pfps/{auth_user_id}.jpg")

    x_dim = img.width
    y_dim = img.height

    # check x and y
    if x_end < x_start or y_end < y_start:
        raise InputError(description="Incorrect crop dimensions")

    xcoords = (x_start, x_end)
    ycoords = (y_start, y_end)

    for coord in xcoords:
        if coord not in range(0, x_dim):
            raise InputError(
                description="X Crop dimensions outside of picture")

    for coord in ycoords:
        if coord not in range(0, y_dim):
            raise InputError(
                description="Y Crop dimensions outside of picture")

    area = (x_start, y_start, x_end, y_end)
    img = img.crop(area)

    img = img.save(f"./src/pfps/{auth_user_id}.jpg")

    for user in store['users']:
        if user[U_ID_IDX] == auth_user_id:
            user[U_PFP_IDX] = f"{BASE_URL}/imgurl/{auth_user_id}.jpg"
    data_store.set(store)
    return {}


def remove_user_v1(auth_user_id, u_id):
    '''
    This function takes in two user id's, one which identifies a
    Seams owner and which identifies a user to be removed from
    seams. The user is then removed and any messages they've sent
    are replaced by 'Removed user'.

    Arguments:
        auth_user_id (int) - A unique id which identifies a user
        u_id (int) - A unique id which identifies a user

    Exceptions:
        InputError  - Occurs when a u_id does not refer to a valid user
        InputError  - Occurs when a u_id refers to a user who is the only global owner
        AccessError  - Occers when the authorised user is not a global owner

    Return Value:
        Returns {}
    '''

    store = data_store.get()
    global_owners = store['global_owner']

    # Checks
    if auth_user_id not in global_owners:
        raise AccessError("the authorised user is not a global owner")
    found = False
    for user in store['users']:
        if user[U_ID_IDX] == u_id:
            found = True
            u_email = user[U_EMAIL_IDX]
            u_handle = user[U_HANDLE_IDX]
    if found is False:
        raise InputError(description="u_id does not refer to a valid user")
    if [u_id] == global_owners:
        raise InputError(
            description="u_id refers to a user who is the only global owner")

    # Implementation
    store['removed_users'].append(u_id)
    store['removed_emails'].append(u_email)
    store['removed_handles'].append(u_handle)

    for user in store['users']:
        if user[U_ID_IDX] == u_id:
            user[U_NAME_FIRST_IDX] = "Removed"
            user[U_NAME_LAST_IDX] = "user"
    # Remove from chs
    channels = store['channels']
    for channel in channels:
        if u_id in channel[CH_OWN_IDX]:
            channel[CH_OWN_IDX].remove(u_id)
        if u_id in channel[CH_MEMBER_IDX]:
            channel[CH_MEMBER_IDX].remove(u_id)

    # Remove from dms

    dms = store['dms']
    for dm in dms:
        removed = None
        # owner of dm
        if u_id == dm[DM_OWN_IDX]['owner_info'][U_ID_IDX]:
            dm[DM_OWN_IDX]['status'] = 'left'

        for member in dm[DM_MEMBERS_IDX]:
            # if for this member the u_id is the same remember the entry
            if u_id == member[U_ID_IDX]:
                removed = member
                break
        # remove the remembered entry from the dm users
        if removed != None:
            dm[DM_MEMBERS_IDX].remove(removed)

    # Change all sent messages to Removed user
    message_lists = (store['messages'], store['dm_messages'])
    for message_list in message_lists:
        for channel in message_list:
            for message in channel:
                if message['u_id'] == u_id:
                    message['message'] = "Removed user"
    # remove token from valid sessions

    sessions = store['sessions']

    for session in sessions:
        curr_uid = jwt.decode(session, SECRET, algorithms=[
                              "HS256"])['auth_user_id']
        if curr_uid == u_id:
            print("HERE")
            sessions.remove(session)

    data_store.set(store)
    return {}


def user_set_handle(auth_user_id, handle_str):
    '''
    The function take in an authorised users id and handle string and updates
    the user's handle (i.e. display name)

    Arguments:
        auth_user_id (int) - A unique id which identifies a user
        handle_str (str) - A string which will be the users new handle

    Exceptions:
        InputError  - Occurs when length of handle_str is not between 3 and 20 characters inclusive
        InputError  - Occurs when handle_str contains characters that are not alphanumeric
        InputError  - Occurs when the handle is already used by another user

    Return Value:
        Returns {}
    '''
    u_id_idx = 0
    u_handle_idx = 5
    store = data_store.get()

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Handle length not within 3-20 inclusive")

    handle_str.replace(" ", "")
    if handle_str.isalnum() is False:
        raise InputError(
            description="Handle contains non alpahnumeric characters")
    for user in store['users']:
        if user[u_handle_idx] == handle_str:
            raise InputError(
                description="Handle is already in user by another user")

    for user in store['users']:
        if user[u_id_idx] == auth_user_id:
            user[u_handle_idx] = handle_str

    for dm in store['dms']:
        if dm[DM_OWN_IDX]['owner_info'][0] == auth_user_id:
            dm[DM_OWN_IDX]['owner_info'][4] = handle_str
            dm[DM_MEMBERS_IDX][-1][4] = handle_str
        else:
            for user in dm[DM_MEMBERS_IDX]:
                if user[0] == auth_user_id:
                    user[4] = handle_str
                    break

    data_store.set(store)
    return {}


def change_userpermission(auth_user_id, u_id, permission_id):
    '''
    Given a user by their user ID, set their permissions to new permissions described by permission_id.
    In:{ token(auth), u_id, permission_id }
    errors:

    Arguments:
        auth_user_id (int) - A unique id which identifies a user
        u_id (int) - A unique id which identifies a user
        permission_id (int) - An integer which defines the user a seams owner or member

    Exceptions:
        InputError  - Occurs when a u_id does not refer to a valid user
        InputError  - Occurs when a u_id refers to a user who is the only
                         global owner and they are being demoted to a user
        InputError  - Occurs when permission_id is invalid
        InputError  - Occurs when the user already has the permissions level of permission_id
        AccessError  - Occers when the authorised user is not a global owner

    Return Value:
        Returns {}
    '''
    id_idx = 0
    store = data_store.get()

    global_owners = store['global_owner']
    if auth_user_id not in global_owners:
        raise AccessError(
            description="The authorised user is not a global owner")
    valid_user = False

    for user in store['users']:
        if user[id_idx] == u_id:
            valid_user = True
            break

    valid_pid = (1, 2)
    if valid_user is False:
        raise InputError(description="u_id does not refer to a valid user")

    elif global_owners == [u_id] and permission_id == 2:
        raise InputError(
            description="u_id refers to a user who is the only global owner and they are being demoted to a user")

    elif permission_id not in valid_pid:
        raise InputError(description="permission_id is invalid")

    elif (permission_id == 1 and u_id in global_owners) or (permission_id == 2 and u_id not in global_owners):
        raise InputError(
            description="the user already has the permissions level of permission_id")
    elif permission_id == 1:
        global_owners.append(u_id)
    else:
        global_owners.remove(u_id)

    data_store.set(store)
    return {}


def user_profile_setname_v1(auth_user_id, name_first, name_last):
    '''
    Takes an authenticated user id, a first name and a last name. 
    The first and last names must be between 1 and 50 characters inclusive.
    The function then updates the authorised users's first and
    last name with the ones inputed.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        name_first (string) - A string with length between 1 and 50 characters inclusive
        name_last (string) - A string with length between 1 and 50 characters inclusive

    Exceptions:
        InputError - Occurs when length of name_first is not 
                        between 1 and 50 characters inclusive
        InputError - Occurs when length of name_last is not 
                        between 1 and 50 characters inclusive

    Return Value:
        Returns {}
    '''
    store = data_store.get()

    if len(name_first) > 50 or len(name_last) > 50:
        raise InputError(
            description="Your first and last names must each be less than 51 characters in length")

    elif len(name_first) == 0 or len(name_last) == 0:
        raise InputError(
            description="You must enter both a first name and a last name")

    else:
        for user in store['users']:
            if user[U_ID_IDX] == auth_user_id:
                user[U_NAME_FIRST_IDX] = name_first
                user[U_NAME_LAST_IDX] = name_last

    for dm in store['dms']:
        if dm[DM_OWN_IDX]['owner_info'][0] == auth_user_id:
            dm[DM_OWN_IDX]['owner_info'][2] = name_first
            dm[DM_OWN_IDX]['owner_info'][3] = name_last
            dm[DM_MEMBERS_IDX][-1][2] = name_first
            dm[DM_MEMBERS_IDX][-1][3] = name_last
        else:
            for user in dm[DM_MEMBERS_IDX]:
                if user[0] == auth_user_id:
                    user[2] = name_first
                    user[3] = name_last
                    break

    data_store.set(store)
    return {}


def user_profile_setemail_v1(auth_user_id, email):
    '''
    Takes an authenticated user id and an email. The
    function then updates the authorised user's email address.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        email (string) - A string which matches the regular expression
                             defined as 'regex' below

    Exceptions:
        InputError - Occurs when the email entered does not match
                         the regular expression defined by 'regex'.
        InputError - Occurs when the email address is already being used by another user.

    Return Value:
        Returns {}
    '''
    store = data_store.get()

    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    match = re.fullmatch(regex, email)

    if match is None:
        raise InputError(description="Invalid email format")

    for user in store['users']:
        if user[U_EMAIL_IDX] == email:
            raise InputError(description="Email already in use")

    else:
        for user in store['users']:
            if user[U_ID_IDX] == auth_user_id:
                user[U_EMAIL_IDX] = email

    for dm in store['dms']:
        if dm[DM_OWN_IDX]['owner_info'][0] == auth_user_id:
            dm[DM_OWN_IDX]['owner_info'][1] = email
            dm[DM_MEMBERS_IDX][-1][1] = email
        else:
            for user in dm[DM_MEMBERS_IDX]:
                if user[0] == auth_user_id:
                    user[1] = email
                    break

    data_store.set(store)
    return {}


def user_profile_v1(user_id, token):
    '''
    Description: 'user_profile_v1' is a function which returns a dictionary of all of a user's 
        information (e.g. user_id, email, first name, last name, and handle).

        It verifies the token passed in within the list of sessions.

        then it creates a dictionary containing the users details.

    Arguments:
        'auth_user_id'    (dictionary) - A dictionary containing the users id.
        'token' - JWT token representing session ID

    Return Value:
        'user_dict' - A dictionary containing the users; user_id, email, first name, last name, and handle.
    '''

    verify_session(token)
    store = data_store.get()
    user_dict = {}
    for user in store['users']:
        if int(user[U_ID_IDX]) == int(user_id):
            user_dict = {'u_id': user_id, 'email': user[U_EMAIL_IDX], 'name_first': user[U_NAME_FIRST_IDX],
                         'name_last': user[U_NAME_LAST_IDX], 'handle_str': user[U_HANDLE_IDX], "profile_img_url": user[U_PFP_IDX]}
            break
    if not user_dict:
        raise InputError(description="u_id does not refer to a valid user")
    return {"user": user_dict}


def user_stats_v1(token):
    '''
    Description: 'user_stats_v1' is a function which returns a dictionary of all of a user's 
        activity (the number of channels and dms joined, and messages sent)

        It verifies the token passed in within the list of sessions.

        then it creates a dictionary containing the users activity.

    Arguments:
        'token' - JWT token representing session ID

    Return Value:
        'user_stats' - A dictionary containing the stats of the user:
            'channels_joined': list of dictionaries
            'dms_joined': list of dictionaries
            'messages_sent': list of dictionaries
            'involvement_rate': float
    '''
    auth_user_id = verify_session(token)
    check_message_send_later(token)

    store = data_store.get()
    for user in store['channel_track']:
        if user['auth_user_id'] == auth_user_id:
            channels_joined = user['channels_joined']
            num_ch_joined = user['channels_joined'][-1]['num_channels_joined']
            # break

    for user in store['dm_track']:
        if user['auth_user_id'] == auth_user_id:
            dms_joined = user['dms_joined']
            num_dms_joined = user['dms_joined'][-1]['num_dms_joined']
            # break

    for user in store['message_track']:
        if user['auth_user_id'] == auth_user_id:
            messages_sent = user['messages_sent']
            num_msgs_sent = user['messages_sent'][-1]['num_messages_sent']
            # break

    numerator = num_ch_joined + num_dms_joined + num_msgs_sent
    # check this below:
    total_num_channels = store['channels_exist'][-1]['num_channels_exist']
    total_num_dms = store['dms_exist'][-1]['num_dms_exist']
    total_num_msgs = store['messages_exist'][-1]['num_messages_exist']

    denom = total_num_channels + total_num_dms + total_num_msgs
    if denom == 0:
        involvement = 0
    else:
        involvement = numerator / denom

    if involvement > 1:
        involvement = 1

    user_stats = {
        'channels_joined': channels_joined,
        'dms_joined': dms_joined,
        'messages_sent': messages_sent,
        'involvement_rate': involvement
    }
    return {
        'user_stats': user_stats
    }

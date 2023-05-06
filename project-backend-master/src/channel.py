'''
channel.py:

This script contains functions which allow users to invite other users to a
channel, view the details of a channel, view
the messages within a channel, leave a channel, join a channel, add an
owner to a channel or remove an owner from a channel.

Functions:
    channel_invite_v1(auth_user_id, channel_id, u_id)
    channel_details_v1(auth_user_id, channel_id)
    channel_messages_v1(auth_user_id, channel_id, start)
    channel_leave_v1(auth_user_id, channel_id)
    channel_join_v1(auth_user_id, channel_id)
    channel_addowner_v1(token, channel_id, u_id)
    channel_removeowner_v1(token, channel_id, u_id)
    
'''
from datetime import datetime
from src import auth
from src.data_store import CH_MEMBER_IDX, CH_ID_IDX, CH_NAME_IDX, CH_OWN_IDX, \
    CH_SET_IDX, U_EMAIL_IDX, U_HANDLE_IDX, U_ID_IDX, \
    U_NAME_FIRST_IDX, U_NAME_LAST_IDX, U_PFP_IDX, data_store
from src.error import InputError
from src.error import AccessError
from src.notifications import generate_notifcation
from src.other import check_channel_id, check_auth_user
from src.verify_session import verify_session
from src.stats import update_ch_stats


def channel_invite_v1(auth_user_id, channel_id, u_id):
    '''
    Takes two authenticated users (auth_user_id and u_id) and a channel id.
    Invites u_id to join the channel, which auth_user_id is already a member of.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        channel_id (int) - A uniqe channel id which identifies each channel
        user_id (int) - The uniqe id of a user who will be invited to a channel

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when u_id does not refer to a valid user
        InputError - Occurs when u_id refers to a user who is already a member of the channel
        AccessError - Occurs when channel_id is valid and the authorised
        user is not a member of the channel

    Return Value:
        Returns {}
    '''
    store = data_store.get()

    # Channel id not existing
    channel = check_channel_id(channel_id)

    # U_id valid user
    uid_exists = False
    for user in store['users']:
        if user[U_ID_IDX] == u_id:
            uid_exists = True
            break

    if uid_exists is False:
        raise InputError(description="Incorrect user_id")

    # Checking if user is apart of chanel (all owners are members)
    if u_id in channel[CH_MEMBER_IDX]:
        raise InputError(description="Already apart of this team")

    # Trying to acces private channel
    if channel[CH_SET_IDX] is False and auth_user_id not in channel[CH_MEMBER_IDX]:
        raise AccessError(description="This is a private channel")

    # Add to channel
    channel[CH_MEMBER_IDX].append(u_id)

    # notifications
    data_store.set(store)
    generate_notifcation(channel_id, -1, 3, auth_user_id,
                         u_id, channel[CH_NAME_IDX], -1)

    # data_store.set(store)
    # Update the channel tracker for the person being invited
    # for user in store['channel_track']:
    #     if user['auth_user_id'] == u_id:
    #         most_recent = user['channels_joined'][-1]
    #         new_num_ch = most_recent['num_channels_joined'] + 1
    #         time_now = int(datetime.timestamp(datetime.now()))
    #         new_dict = {
    #             'num_channels_joined': new_num_ch,
    #             'time_stamp': time_now,
    #         }
    #         user['channels_joined'].append(new_dict)
    #         break
    update_ch_stats(u_id, True)

    return {}


def channel_details_v1(auth_user_id, channel_id):
    '''
    Takes an authenticated user id and an authenticated channel id which the user is a
    member of and returns basic details about the channel (channel name, public
    or private, channel owners, all channel members)

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        channel_id (int) - A uniqe channel id which identifies each channel

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        AccessError - Channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns name (str), is_public(bool), owner_members(list of dictionaries),
         all_members(list of dictionaries)
    '''

    store = data_store.get()

    # Channel id not existing (assuming it is given as an int)
    channel = check_channel_id(channel_id)

    # Checking member of channel or is global
    if auth_user_id not in channel[CH_MEMBER_IDX]:
        raise AccessError(description="Not a member of the channel")

    member_list = channel[CH_MEMBER_IDX][:]
    owner_list = channel[CH_OWN_IDX][:]
    users = store['users']

    # Replacing number lists with actual details
    for idx, owner_id in enumerate(owner_list):
        for entry in users:
            if entry[U_ID_IDX] == owner_id:
                owner_list[idx] = entry

    for idx, member_id in enumerate(member_list):
        for entry in users:
            if entry[U_ID_IDX] == member_id:
                member_list[idx] = entry

    # Making the lists into dictionaries for the output as per given example
    user_dict = {}

    dbl = (owner_list, member_list)
    for list_entry in dbl:
        for idx, user in enumerate(list_entry):
            user_dict = {}
            user_dict['u_id'] = user[U_ID_IDX]
            user_dict['email'] = user[U_EMAIL_IDX]
            user_dict['name_first'] = user[U_NAME_FIRST_IDX]
            user_dict['name_last'] = user[U_NAME_LAST_IDX]
            user_dict['handle_str'] = user[U_HANDLE_IDX]
            user_dict['profile_img_url'] = user[U_PFP_IDX]
            list_entry[idx] = user_dict

    return {
        'name': channel[CH_NAME_IDX],
        'is_public': channel[CH_SET_IDX],
        'owner_members': owner_list,
        'all_members': member_list,
    }


def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    Takes an authorised user id, a channel id which the user is a
    member of and a start value.  Returns up to 50 messages from most recent to least
    recent between index 'start' and 'start + 50'. If the least recent message is
    returned, -1 is returned in 'end' to indiciate no further messages are available.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        channel_id (int) - A uniqe channel id which identifies each channel
        start (int) - The first message (in order of recency) the user would like to view

    Exceptions:
        AccessError - Occurs when Channel_id is valid and the authorised user is not a member of the channel
        InputError - Occurs when channel_id does not refer to a valid channel
        InputError - Occurs when start is greater than the total number of messages in the channel

    Return Value:
        Returns messages(list of dictionaries), start(int), end(int)
    '''
    store = data_store.get()

    # Helper function to check if ID is valid
    channel = check_channel_id(channel_id)

    if auth_user_id not in channel[CH_MEMBER_IDX]:
        raise AccessError(description="You are not a member of this channel")

    total_messages = len(store['messages'][channel_id])

    if total_messages == 0 and start > total_messages:
        raise InputError(
            description="There are no messages in this channel, start must be set to 0")

    if total_messages != 0 and start >= total_messages:
        raise InputError(
            description="You have set a start larger than the total number of messages")

    page_of_messages = []
    time_now = int(datetime.timestamp(datetime.now()))
    for idx, message in enumerate(reversed(store['messages'][channel_id])):
        if start <= idx < start + 50:
            if message['time_sent'] <= time_now:
                page_of_messages.append(message)

    if total_messages - start < 50:
        end = -1
    else:
        end = start + 50

    for msg_idx, message in enumerate(page_of_messages):
        for r_idx, react in enumerate(message['reacts']):
            for u_id in react['u_ids']:
                if u_id == auth_user_id:
                    page_of_messages[msg_idx]['reacts'][r_idx]['is_this_user_reacted'] = True
                else:
                    page_of_messages[msg_idx]['reacts'][r_idx]['is_this_user_reacted'] = False

    data_store.set(store)
    return {
        'messages': page_of_messages,
        'start': start,
        'end': end,
    }


def channel_leave_v1(auth_user_id, channel_id):
    '''
    Takes an authorised user id and a channel id which the user is a
    member of.  Removes the user from the channel.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        channel_id (int) - A uniqe channel id which identifies each channel

    Exceptions:
        AccessError - Channel_id is valid but the authorised user is not a member of the channel
        InputError - Occurs when channel_id does not refer to a valid channel

    Return Value:
        Returns an empty dictionary
    '''
    store = data_store.get()

    # Helper function to check if ID is valid
    channel = check_channel_id(channel_id)

    if auth_user_id not in channel[CH_MEMBER_IDX]:
        raise AccessError(description="You are not a member of this channel")

    else:
        channel[CH_MEMBER_IDX].remove(auth_user_id)

    if auth_user_id in channel[CH_OWN_IDX]:
        channel[CH_OWN_IDX].remove(auth_user_id)

    data_store.set(store)
    update_ch_stats(auth_user_id, False)
    return {}


def channel_join_v1(auth_user_id, channel_id):
    '''
    Takes an authenticated user id and an authenticated channel id and
    adds the user to that channel, unless the channel
    is private and the user is not a global owner.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        channel_id(int) - A uniqe channel id which identifies each channel

    Exceptions:
        InputError - Occurs when channel_id does not refer to a valid channel
        Inputerror - Occurs when the authorised user is already a member of the channel
        AccessError - Occurs when channel_id refers to a channel that is private and the authorised
                        user is not already a channel member and is not a global owner

    Return Value
        Returns {}
    '''
    store = data_store.get()

    # Channel id not existing (assuming it is given as an int)
    channel = check_channel_id(channel_id)

    # Already a member of the channels
    is_in_ch = False
    if auth_user_id in channel[CH_OWN_IDX] or auth_user_id in channel[CH_MEMBER_IDX]:
        is_in_ch = True
        raise InputError(description="Already apart of this team")

    # Trying to acces private channel or is globabl owner
    if is_in_ch is False and channel[CH_SET_IDX] is False and auth_user_id not in store['global_owner']:
        raise AccessError(description="This is a private channel")

    # Add to channel
    channel[CH_MEMBER_IDX].append(auth_user_id)
    data_store.set(store)
    update_ch_stats(auth_user_id, True)
    return {}


def channel_addowner_v1(token, channel_id, u_id):
    '''
    This function adds a new owner to the channel
    Takes in the jwt of an existing owner of the channel
    Given the channel_id and a u_id of an existing member, promote that member

    Arguments:
        token (string) - Token of an owner of the channel
        channel_id (int) - Channel identifier integer
        u_id (int) - u_id of a member of the channel

    Exception:
        Input Error: Occurs when channel_id is invalid
        Input Error: Occurs when u_id does not refer to a valid user
        Input Error: Occurs when u_id doesn't belong to a member of the channel
        Input Error: Occurs when u_id belongs to a current owner of the channel
        Access Error: Occures when channel_id is valid but the user does not
                        have owner permissions in the channel

    Return Value:
        Returns {}
    '''
    caller_id = verify_session(token)
    store = data_store.get()

    check_channel_id(channel_id)

    check_auth_user(u_id)

    # Allows global owner to add themselves to list of owners
    global_owner_trig = False
    owner_valid = False
    global_member = False
    corr_channel = None
    if caller_id in store['global_owner']:
        global_owner_trig = True

    for channel in store['channels']:
        if channel[CH_ID_IDX] == channel_id:
            corr_channel = channel

    if caller_id in corr_channel[CH_OWN_IDX]:
        owner_valid = True
    elif caller_id in corr_channel[CH_MEMBER_IDX] and global_owner_trig == True:
        global_member = True
    else:
        raise AccessError(description='This user is not authorised to call')

    if u_id not in corr_channel[CH_MEMBER_IDX]:
        raise InputError(
            description='This u_id does not belong to a member of the channel')

    if u_id in corr_channel[CH_OWN_IDX]:
        raise InputError(
            description='This member is already an owner of the channel')

    if owner_valid == True or global_member == True:
        corr_channel[CH_OWN_IDX].append(u_id)

    data_store.set(store)
    return {}


def channel_removeowner_v1(token, channel_id, u_id):
    '''
    This function removes an existing owner to the channel
    Takes in the jwt of an existing owner of the channel
    Given the channel_id and a u_id of an existing owner, remove that owner

    Parameters:
        token (string) - Token of an owner of the channel
        channel_id (int) - Channel identifier integer
        u_id (int) - u_id of another owner of the channel

    Exception:
        Input Error: Occurs when channel_id is invalid
        Input Error: Occurs when u_id does not refer to a valid user
        Input Error: Occurs when u_id doesn't belong to a member of the channel
        Input Error: Occurs when u_id belongs to a current owner of the channel
        Access Error: Occures when channel_id is valid but the user does not
                        have owner permissions in the channel

    Return Value:
        Returns {}
    '''
    caller_id = verify_session(token)
    store = data_store.get()

    check_channel_id(channel_id)

    check_auth_user(u_id)

    # Allows global owner to add themselves to list of owners
    global_owner_trig = False
    owner_valid = False
    global_member = False
    corr_channel = None
    if caller_id in store['global_owner']:
        global_owner_trig = True

    for channel in store['channels']:
        if channel[CH_ID_IDX] == channel_id:
            corr_channel = channel

    if caller_id in corr_channel[CH_OWN_IDX]:
        owner_valid = True
    elif caller_id in corr_channel[CH_MEMBER_IDX] and global_owner_trig == True:
        global_member = True
    else:
        raise AccessError(description='This user is not authorised to call')

    if u_id not in corr_channel[CH_OWN_IDX]:
        raise InputError(
            description='This u_id does not belong to an owner of the channel')

    if len(corr_channel[CH_OWN_IDX]) == 1:
        raise InputError(description='Cannot remove only owner of the channel')

    if owner_valid == True or global_member == True:
        corr_channel[CH_OWN_IDX].remove(u_id)

    data_store.set(store)

    return {}

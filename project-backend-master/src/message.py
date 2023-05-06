'''
message.py:

This script contains functions which allow users to view lists of channel
members, channel owerns and to create new channels.

Functions:
    message_pin_unpin(token, message_id, is_pinned)
    message_send_v1(token, channel_id, message, share)
    message_senddm_v1(token, dm_id, message, share)
    message_sendlater_v1(token, channel_id, message, time_sent)
    message_sendlaterdm_v1(token, dm_id, message, time_sent)
    check_message_send_later(token)
    message_edit_v1(token, message_id, message)
    message_react_unreact_v1(token, message_id, react_id, unreact)
    message_share_v1(token, og_message_id, message, channel_id, dm_id)
'''

from email import message
from os import access
from src.notifications import generate_notifcation
from src.data_store import CH_ID_IDX, CH_MEMBER_IDX, CH_NAME_IDX, CH_OWN_IDX, \
    DM_ID_IDX, DM_MEMBERS_IDX, DM_NAME_IDX, DM_OWN_IDX, M_U_ID_IDX, U_ID_IDX, data_store, U_HANDLE_IDX
from src.error import InputError, AccessError
from datetime import datetime
from src.verify_session import verify_session
from src.stats import update_msgs_stats, update_workplace_msg_stats


def message_pin_unpin(token, message_id, is_pinned):
    ''' 
    Given a message within a channel or DM, mark it as "pinned" or 
    Given a message within a channel or DM, remove its mark as pinned,
    depending on the instance where it is called and the is_pinned variable

    Input:
        - Token (str)
        - Message_id (int)
    Return:
         -{}
    errors:

    For pinning:

    InputError when:
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        the message is already pinned

    AccessError when:
        - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM

    For unpinning:

    InputError when any of:
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        the message is not already pinned

      AccessError when:
        - message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM

    '''
    # is_pinned = TRUE = pin
    # is_pinned = False = unpin
    store = data_store.get()
    auth_id = verify_session(token)

    message_lists = (store['messages'], store['dm_messages'])
    message_found = False
    raise_error = False
    inputerror = "Invalid message id"
    accesserror = ""
    found_entry = None
    message_loc = 0
    # Checking both ch and dm messages
    for message_list in message_lists:
        # Checking within a list for ch or dm
        for idx, channel in enumerate(message_list):
            for message in channel:
                if message['message_id'] == message_id and message['is_pinned'] != is_pinned:
                    message_found = True
                    found_entry = message
                    loc_id = idx
                    message_loc = message_list
                elif message['message_id'] == message_id and message['is_pinned'] == is_pinned:
                    inputerror = "Message already pinned!"
                    message_found = True
                    raise_error = True
                    loc_id = idx
                    message_loc = message_list

    if message_found == False:
        raise_error = True
    # do acces error check
    if message_loc == store['messages']:
        for channel in store['channels']:
            if channel[CH_ID_IDX] == loc_id and auth_id not in channel[CH_OWN_IDX]:
                raise_error = True
                accesserror = "You are not authorised to pin this dm"
    elif message_loc == store['dm_messages']:
        for dm in store['dms']:
            if dm[DM_ID_IDX] == loc_id and auth_id != dm[DM_OWN_IDX]['owner_info'][0]:
                raise_error = True
                accesserror = "You are not authorised to pin this dm"
    #raise erros
    if raise_error == True and accesserror != "":
        raise AccessError(description=accesserror)
    elif raise_error == True:
        raise InputError(description=inputerror)
    # pin/unpin
    # if found_entry['is_pinned'] != is_pinned:
    found_entry['is_pinned'] = is_pinned

    data_store.set(store)
    return {}


def message_send_v1(token, channel_id, message, share):
    '''
    Take in an authenticated token, channel id and message, send the message to the channel, then
    return the message_id of the message just sent.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        channel_id (int) - The id of the channel the messsge is directed to
        message (str) - The message to be sent

    Exceptions: 
        AccessError - Occurs when the token is not valid.
                    - The user associated with the token is not a member of the channel
        InputError  - Occurs when channel_id is invalid
                    - Occurs when the length of the message is 0 or greater than 1000 characters

    Return value:
        message_id (int)
    '''
    auth_id = verify_session(token)
    store = data_store.get()

    ch_id_idx = 0
    ch_member_idx = 4
    valid_ch_id = False
    in_channel = False
    # Validating channel
    for channel in store['channels']:
        if channel[ch_id_idx] == channel_id:
            valid_ch_id = True
            for user_id in channel[ch_member_idx]:
                if user_id == auth_id:
                    in_channel = True
                    break
            break

    if valid_ch_id is False:
        raise InputError(
            description="Invalid channel id: Does not refer to a valid channel")

    if in_channel is False:
        raise AccessError(
            description="This user is not a member of the channel")

    if share == False:
        if len(message) == 0 or len(message) > 1000:
            raise InputError(description="Invalid message length: Cannot be less than 1 character or greater\
                than 1000 characters")

    # Generate message id and store message data in the data store:
    message_id = store['message_counter'] + 1
    store['message_counter'] = message_id
    time_sent = int(datetime.timestamp(datetime.now()))

    reacts_data = []

    message_data = {
        'message_id': message_id,
        'u_id': auth_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': reacts_data,
        'is_pinned': False
    }

    tags = generate_tag(message)
    data_store.set(store)
    # generates notifications for everone tagged in the message
    for handle in tags:
        # find user in data store and then generate notifcation
        for user in store['users']:
            if user[U_HANDLE_IDX] == handle:
                generate_notifcation(channel[CH_ID_IDX], -1,
                                     1, auth_id, user[U_ID_IDX], channel[CH_NAME_IDX], message)

    store['messages'][channel_id].append(message_data)
    data_store.set(store)

    update_msgs_stats(auth_id, time_sent)
    update_workplace_msg_stats(True, 1)
    return {
        'message_id': message_id,
    }


def message_senddm_v1(token, dm_id, message, share):
    '''
    Take in an authenticated token, dm id and message, send the message to the dm, then
    return the message_id of the message just sent.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        dm_id (int) - The id of the dm the messsge is directed to
        message (str) - The message to be sent

    Exceptions: 
        AccessError - Occurs when the token is not valid.
                    - The user associated with the token is not a member of the channel
        InputError  - Occurs when dm_id is invalid
                    - Occurs when the length of the message is 0 or greater than 1000 characters

    Return value:
        message_id (int)
    '''
    auth_id = verify_session(token)
    store = data_store.get()
    DM_M_ID_IDX = 0
    valid_dm_id = False
    in_dm = False
    # Check if the provided dm_id is valid, and if the user is in it
    for dm in store['dms']:
        if dm[DM_ID_IDX] == dm_id:
            valid_dm_id = True
            for user_id in dm[DM_MEMBERS_IDX]:
                if user_id[DM_M_ID_IDX] == auth_id:
                    in_dm = True
                    break
            break

    if valid_dm_id is False:
        raise InputError(
            description="Invalid dm id: Does not refer to a valid dm")

    if in_dm is False:
        raise AccessError(description="This user is not a member of the dm")

    if share == False:
        if len(message) == 0 or len(message) > 1000:
            raise InputError(description="Invalid message length: Cannot be less than 1 character or greater\
                than 1000 characters")

    # Generate message id and store message data in the data store:
    message_id = store['message_counter'] + 1
    store['message_counter'] = message_id
    time_sent = int(datetime.timestamp(datetime.now()))

    reacts_data = []
    message_data = {
        'message_id': message_id,
        'u_id': auth_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': reacts_data,
        'is_pinned': False,
    }

    tags = generate_tag(message)
    data_store.set(store)
    # generates notifications for everone tagged in the message
    for handle in tags:
        # find user in data store and then generate notifcation
        for user in store['users']:
            if user[U_HANDLE_IDX] == handle:
                generate_notifcation(-1, dm[DM_ID_IDX],
                                     1, auth_id, user[U_ID_IDX], dm[DM_NAME_IDX], message)

    store['dm_messages'][dm_id].append(message_data)
    data_store.set(store)
    update_msgs_stats(auth_id, time_sent)
    update_workplace_msg_stats(True, 1)
    return {
        'message_id': message_id,
    }


def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Take in an authenticated token, channel id, message and time, send the message
    to the channel at the specified time, then return the message_id of the message just sent.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        channel_id (int) - The id of the channel the messsge is directed to
        message (str) - The message to be sent
        time_sent (int) - The time in the future at which the message is sent/becomes valid

    Exceptions: 
        AccessError - Occurs when the token is not valid.
                    - The user associated with the token is not a member of the channel
        InputError  - Occurs when channel_id is invalid
                    - Occurs when the length of the message is 0 or greater than 1000 characters
                    - Occurs when time_sent is in the past

    Return value:
        message_id (int)
    '''
    auth_id = verify_session(token)
    store = data_store.get()
    ch_id_idx = 0
    ch_member_idx = 4
    valid_ch_id = False
    in_channel = False
    # Validating channel
    for channel in store['channels']:
        if channel[ch_id_idx] == channel_id:
            valid_ch_id = True
            for user_id in channel[ch_member_idx]:
                if user_id == auth_id:
                    in_channel = True
                    break
            break

    if valid_ch_id is False:
        raise InputError(
            description="Invalid channel id: Does not refer to a valid channel")

    if in_channel is False:
        raise AccessError(
            description="This user is not a member of the channel")

    if len(message) == 0 or len(message) > 1000:
        raise InputError(description="Invalid message length: Cannot be less than 1 character or greater\
            than 1000 characters")

    time_now = int(datetime.timestamp(datetime.now()))

    if time_sent < time_now:
        raise InputError(
            description="Invalid time_sent. It cannot be in the past")
    # Generate message id and store message data in the data store:
    message_id = store['message_counter'] + 1
    store['message_counter'] = message_id

    reacts_data = []

    message_data = {
        'message_id': message_id,
        'u_id': auth_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': reacts_data,
        'is_pinned': False,
    }
    msg_info = {
        'channel': True,
        'location_id': channel_id,
        'message_data': message_data,
    }

    tags = generate_tag(message)
    data_store.set(store)
    # generates notifications for everone tagged in the message

    for handle in tags:
        # find user in data store and then generate notifcation
        for user in store['users']:
            if user[U_HANDLE_IDX] == handle:
                generate_notifcation(channel[CH_ID_IDX], -1,
                                     1, auth_id, user[U_ID_IDX], channel[CH_NAME_IDX], message)

    store['messages_later'].append(msg_info)
    data_store.set(store)

    return {
        'message_id': message_id,
    }


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Take in an authenticated token, dm id, message and time, send the message to the dm at the specified time,
    then return the message_id of the message just sent.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        dm_id (int) - The id of the dm the messsge is directed to
        message (str) - The message to be sent
        time_sent (int) - The time in the future at which the message is sent/becomes valid

    Exceptions: 
        AccessError - Occurs when the token is not valid.
                    - The user associated with the token is not a member of the channel
        InputError  - Occurs when dm_id is invalid
                    - Occurs when the length of the message is 0 or greater than 1000 characters
                    - Occurs when time_sent is in the past

    Return value:
        message_id (int)
    '''
    auth_id = verify_session(token)
    store = data_store.get()
    DM_M_ID_IDX = 0
    valid_dm_id = False
    in_dm = False
    # Check if the provided dm_id is valid, and if the user is in it
    for dm in store['dms']:
        if dm[DM_ID_IDX] == dm_id:
            valid_dm_id = True
            for user_id in dm[DM_MEMBERS_IDX]:
                if user_id[DM_M_ID_IDX] == auth_id:
                    in_dm = True
                    break
            break

    if valid_dm_id is False:
        raise InputError(
            description="Invalid dm id: Does not refer to a valid dm")

    if in_dm is False:
        raise AccessError(description="This user is not a member of the dm")

    # Check if the string length is valid:
    if len(message) == 0 or len(message) > 1000:
        raise InputError(description="Invalid message length: Cannot be less than 1 character or greater\
            than 1000 characters")
    time_now = int(datetime.timestamp(datetime.now()))
    if time_sent < time_now:
        raise InputError(
            description="Invalid time_sent. It cannot be in the past")

    # Generate message id and store message data in the data store:
    message_id = store['message_counter'] + 1
    store['message_counter'] = message_id

    reacts_data = []

    message_data = {
        'message_id': message_id,
        'u_id': auth_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': reacts_data,
        'is_pinned': False,
    }
    msg_info = {
        'channel': False,
        'location_id': dm_id,
        'message_data': message_data,
    }
    tags = generate_tag(message)
    data_store.set(store)

    for handle in tags:
        # find user in data store and then generate notifcation
        for user in store['users']:
            if user[U_HANDLE_IDX] == handle:
                generate_notifcation(-1, dm[DM_ID_IDX],
                                     1, auth_id, user[U_ID_IDX], dm[DM_NAME_IDX], message)

    store['messages_later'].append(msg_info)
    data_store.set(store)

    return {
        'message_id': message_id,
    }


def check_message_send_later(token):
    '''
    Helper function that checks whether any messages are ready to be sent to a channel yet.
    This should be called before any function that adds things to messages to see if there
    should be any messages in a queue that need to be sent beforehand.

    Arguments:
        token (str) - A unique token which identifies an authenticated user

    Exceptions: 
        AccessError - Occurs when the token is not valid.

    Return value:
        Null  
    '''
    verify_session(token)
    store = data_store.get()
    msgs = store['messages_later']
    # sort based on the time sent
    now = int(datetime.timestamp(datetime.now()))
    sorted_msgs = sorted(msgs, key=lambda x: x['message_data']['time_sent'])

    for message in sorted_msgs:
        # send the message if the time has passed.
        if message['message_data']['time_sent'] <= now:
            time_sent = message['message_data']['time_sent']
            location_id = message['location_id']
            sender_id = message['message_data']['u_id']
            if message['channel'] is True and len(message['message_data']['message']) > 0:
                store['messages'][location_id].append(message['message_data'])
                data_store.set(store)
                update_msgs_stats(sender_id, time_sent)
                update_workplace_msg_stats(True, 1)
            if message['channel'] is False:
                dm_id = message['location_id']
                # check if dm has been removed. If it hasn't send the message
                if len(store['dms'][dm_id - 1][DM_MEMBERS_IDX]) != 0:
                    store['dm_messages'][location_id].append(
                        message['message_data'])
                    data_store.set(store)
                    update_msgs_stats(sender_id, time_sent)
                    update_workplace_msg_stats(True, 1)
            store['messages_later'].remove(message)

    data_store.set(store)

    return {}


def message_edit_v1(token, message_id, message):
    '''
    Take in an authenticated token, message id and a new message, and edit the old message
    to be the new message. If the new message is empty, delete the message and its associated
    details.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        message_id (int) - The id of the messsge to be changed
        message (str) - The new message

    Exceptions: 
        AccessError - Occurs when the token is not valid.
                    - The user associated with the token does not have permissions to change the
                    original message
        InputError  - Occurs when message_id is invalid
                    - Occurs when the length of the message is greater than 1000 characters

    Return value:
        {}
    '''
    store = data_store.get()
    auth_id = verify_session(token)
    # check if the message is of a valid length
    if len(message) > 1000:
        raise InputError(
            description="Invalid message length: Exceeds character limit of 1000")

    # Check if the message id is valid in channel messages
    valid_message_id_ch = False

    channel_counter = 0
    for channel in store['messages']:
        for message_dict in channel:
            # print(message_dict['message_id'])
            # print(message_id)
            if message_dict['message_id'] == message_id:
                valid_message_id_ch = True
                u_id = message_dict['u_id']
                #time_msg = message_dict['time_sent']
                channel_id = channel_counter
                break
        channel_counter += 1

    # Check if the message id is valid in dm messages
    valid_message_id_dm = False
    dm_counter = 0
    for dm in store['dm_messages']:
        for message_dict in dm:
            if message_dict['message_id'] == message_id:
                valid_message_id_dm = True
                u_id = message_dict['u_id']
                #time_msg = message_dict['time_sent']
                dm_id = dm_counter
                break
        dm_counter += 1

    if (valid_message_id_ch == False) and (valid_message_id_dm == False):
        raise InputError(description="Invalid message id")

    is_creator_of_msg = False
    is_owner = False
    if auth_id in store['global_owner']:
        is_owner = True
    # Check if the person making the request is an owner of the channel or dm
    if valid_message_id_ch == True:
        ch_id_idx = 0
        ch_own_idx = 3
        for channels in store['channels']:
            if channels[ch_id_idx] == channel_id:
                for owner in channels[ch_own_idx]:
                    if owner == auth_id:
                        is_owner = True

    if valid_message_id_dm == True:
        dm_id_idx = 0
        dm_own_idx = 1
        for dm in store['dms']:
            if dm[dm_id_idx] == dm_id:
                if dm[dm_own_idx]['owner_info'][0] == auth_id:
                    is_owner = True

    if auth_id == u_id:
        is_creator_of_msg = True

    if (is_creator_of_msg is False) and (is_owner is False):
        raise AccessError(
            description="Unauthorised user attempting to make change to a message")

    if len(message) == 0:
        message_remove_v1(token, message_id)
        return {}

    if valid_message_id_ch == True:
        for channel in store['messages']:
            for message_dict in channel:
                if message_dict['message_id'] == message_id:
                    message_dict['message'] = message

                    tags = generate_tag(message)
                    # generates notifications for everone tagged in the message
                    data_store.set(store)
                    for handle in tags:
                        # find user in data store and then generate notifcation
                        for user in store['users']:
                            if user[U_HANDLE_IDX] == handle:
                                generate_notifcation(
                                    channel_id, -1, 1, auth_id, user[U_ID_IDX], channels[CH_NAME_IDX], message)

    if valid_message_id_dm == True:
        for dm in store['dm_messages']:
            for message_dict in dm:
                if message_dict['message_id'] == message_id:
                    message_dict['message'] = message
                    tags = generate_tag(message)
                    # generates notifications for everone tagged in the message
                    data_store.set(store)
                    for handle in tags:
                        # find user in data store and then generate notifcation
                        for user in store['users']:
                            if user[U_HANDLE_IDX] == handle:
                                generate_notifcation(
                                    -1, dm[DM_ID_IDX], 1, auth_id, user[U_ID_IDX], dm[DM_NAME_IDX], message)

                    break

    data_store.set(store)
    return {}


def message_remove_v1(token, message_id):
    '''
    Take in an authenticated token and message id, and delete the message and its
    associated details

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        message_id (int) - The id of the messsge to be changed

    Exceptions: 
        AccessError - Occurs when the token is not valid.
                    - The user associated with the token does not have permissions to change the
                    original message
        InputError  - Occurs when message_id is invalid

    Return value:
        {}
    '''
    auth_id = verify_session(token)
    store = data_store.get()

    # Check if the message id is valid in channel messages
    valid_message_id_ch = False

    channel_counter = 0
    for channel in store['messages']:
        for message_dict in channel:
            if message_dict['message_id'] == message_id:
                valid_message_id_ch = True
                u_id = message_dict['u_id']
                channel_id = channel_counter
                message = message_dict['message']
                time_sent = message_dict['time_sent']
                is_pinned = message_dict['is_pinned']
                break
        channel_counter += 1

    # Check if the message id is valid in dm messages
    valid_message_id_dm = False
    dm_counter = 0
    for dm in store['dm_messages']:
        for message_dict in dm:
            if message_dict['message_id'] == message_id:
                valid_message_id_dm = True
                u_id = message_dict['u_id']
                dm_id = dm_counter
                message = message_dict['message']
                time_sent = message_dict['time_sent']
                is_pinned = message_dict['is_pinned']
                break
        dm_counter += 1

    if valid_message_id_ch == False and valid_message_id_dm == False:
        raise InputError(description="Invalid message id")

    is_creator_of_msg = False
    is_owner = False
    if auth_id in store['global_owner']:
        is_owner = True
    # Check if the person making the request is an owner of the channel or dm
    if valid_message_id_ch == True:
        ch_id_idx = 0
        ch_own_idx = 3
        for channels in store['channels']:
            if channels[ch_id_idx] == channel_id:
                for owner in channels[ch_own_idx]:
                    if owner == auth_id:
                        is_owner = True

    if valid_message_id_dm == True:
        dm_id_idx = 0
        dm_own_idx = 1
        for dm in store['dms']:
            if dm[dm_id_idx] == dm_id:
                if dm[dm_own_idx]['owner_info'][0] == auth_id:
                    is_owner = True

    if auth_id == u_id:
        is_creator_of_msg = True

    if (is_creator_of_msg is False) and (is_owner is False):
        raise AccessError(
            description="Unauthorised user attempting to make change to a message")

    reacts_data = []

    message_remove = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': reacts_data,
        'is_pinned': is_pinned,
    }
    if valid_message_id_ch == True:
        store['messages'][channel_id].remove(message_remove)
    if valid_message_id_dm == True:
        store['dm_messages'][dm_id].remove(message_remove)

    data_store.set(store)
    update_workplace_msg_stats(False, 1)
    return {}


def message_react_unreact_v1(token, message_id, react_id, unreact):
    '''
    Take in an authenticated token, message id and react_id
    and sets the messages react_id to the react_id passed in.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        message_id (int) - The id of the messsge to be changed
        react_id (int) - An integer which defines a reaction type
        unreact (bool) - If unreact is True, the function is being called
                            to unreact a message rather than react it

    Exceptions: 
        InputError  - Occurs when message_id is not a valid message 
                        within a channel or DM that the authorised user has joined
        InputError  - Occurs when react_id is not a valid react ID - currently, 
                        the only valid react ID the frontend has is 1
        InputError  - Occurs when the message already contains a react with 
                            ID react_id from the authorised user

    Return value:
        {}
    '''
    DM_MEM_ID_IDX = 0
    store = data_store.get()
    auth_id = verify_session(token)

    message_lists = (store['messages'], store['dm_messages'])
    msg_found = False

    for message_list in message_lists:
        for idx, ch_dm in enumerate(message_list):
            for idx2, message in enumerate(ch_dm):
                if message['message_id'] == message_id:
                    msg_found = True
                    msg_loc = message_list
                    loc_idx = idx
                    msg_idx = idx2
                    reacts = message['reacts']
                    author = message['u_id']

    if msg_found == False:
        raise InputError(description="This is an invalid message_id")

    for channel in store['channels']:
        if channel[CH_ID_IDX] == loc_idx:
            channel_found = channel
            if auth_id not in channel[CH_MEMBER_IDX] and auth_id is not store['global_owner']:
                raise InputError(
                    description="This message is in a channel which you are not a member of")

    is_member = False
    for dm in store['dms']:
        if dm[DM_ID_IDX] == loc_idx:
            dm_found = dm
            for member in dm[DM_MEMBERS_IDX]:
                if member[DM_MEM_ID_IDX] == auth_id:
                    is_member = True
            if is_member == False and auth_id is not store['global_owner']:
                raise InputError(
                    description="This message is in a dm which you are not a member of")

    if reacts == []:
        users = []
    else:
        for react in reacts:
            if react['react_id'] == react_id:
                users = react['u_ids']
            else:
                users = []

    if unreact == False:
        if auth_id in users:
            raise InputError(
                description='You have already added this react to this message')
    else:
        if auth_id not in users:
            raise InputError(
                description='You have not added a react to this message')

    users.append(auth_id)

    if react_id not in store['valid_reacts']:
        raise InputError(description="We haven't implemented this react yet!")

    react_data = {
        'react_id': react_id,
        'u_ids': users,
        'is_this_user_reacted': True
    }

    if msg_loc == store['messages']:
        store['messages'][loc_idx][msg_idx]['reacts'].append(react_data)
        channel_id = loc_idx
        data_store.set(store)
        generate_notifcation(channel_id, -1, 2, auth_id,
                             author, channel_found[CH_NAME_IDX], -1)

    else:
        store['dm_messages'][loc_idx][msg_idx]['reacts'].append(react_data)
        dm_id = loc_idx
        data_store.set(store)
        generate_notifcation(-1, dm_id, 2, auth_id,
                             author, dm_found[DM_NAME_IDX], -1)

    data_store.set(store)
    return {}


def generate_tag(message_words):
    # This is the process of deconstructing the message and creating a list of all members who are tagged
    message_words = message_words.split()
    tags = []
    tagged = ''
    for word in message_words:
        if "@" in word:
            tags.append(word)

    for x in tags:
        tagged += x
    tags = tagged.split("@")
    tags.pop(0)

    # Remove duplicate tags
    tags = list(dict.fromkeys(tags))

    return tags


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Take in an authenticated token, message id and react_id
    and sets the messages react_id to the react_id passed in.

    Arguments:
        token (str) - A unique token which identifies an authenticated user
        og_message_id (int) - The id of the messsge to be shared
        message (str) - A message which can accompany the message being shared
        channel_id (int) - The channel the message will be sent to. -1 if the message
                                is being sent to a dm
        dm_id (int) - The dm the message will be sent to. -1 if the message is
                            being sent to a channel

    Exceptions: 
        InputError  - Occurs when both channel_id and dm_id are invalid
        InputError  - Occurs when neither channel_id nor dm_id are -1
        InputError  - Occurs when og_message_id does not refer to a valid
                        message within a channel/DM that the authorised user has joined
        InputError  - Occurs when length of message is more than 1000 characters
        AcessError  - Occurs when the pair of channel_id and dm_id are valid
                        (i.e. one is -1, the other is valid) and the authorised
                        user has not joined the channel or DM they are trying
                        to share the message to

    Return value:
        {shared_message_id}
    '''
    DM_MEM_ID_IDX = 0
    store = data_store.get()
    auth_id = verify_session(token)

    ch_found = False
    for ch in store['channels']:
        if ch[CH_ID_IDX] == channel_id:
            ch_found = True
            ch_share = ch

    dm_found = False
    for dm in store['dms']:
        if dm[DM_ID_IDX] == dm_id:
            dm_found = True
            dm_share = dm

    channels_joined = []
    for ch in store['channels']:
        if auth_id in ch[CH_MEMBER_IDX]:
            channels_joined.append(ch[CH_ID_IDX])

    dms_joined = []
    for dm in store['dms']:
        for member in dm[DM_MEMBERS_IDX]:
            if member[DM_MEM_ID_IDX] == auth_id:
                dms_joined.append(dm[DM_ID_IDX])

    if ch_found == True and dm_id == -1 and channel_id not in channels_joined:
        raise AccessError(
            description="You have not joined the channel you are trying\
                             to share a message to")

    if dm_found == True and channel_id == -1 and dm_id not in dms_joined:
        raise AccessError(
            description="You have not joined the dm you are trying\
                             to share a message to")

    msg_found = False
    for idx, ch in enumerate(store['messages']):
        if idx in channels_joined:
            for msg in ch:
                if msg['message_id'] == og_message_id:
                    msg_found = True
                    og_message = msg['message']

    for idx, dm in enumerate(store['dm_messages']):
        if idx in dms_joined:
            for msg in dm:
                if msg['message_id'] == og_message_id:
                    msg_found = True
                    og_message = msg['message']

    if msg_found == False:
        raise InputError(
            description="og_message_id does not refer to a valid\
                            message within a channel/DM which you have joined")

    if dm_found is False and ch_found is False:
        raise InputError(
            description="Both channel_id and dm_id are invalid")

    if dm_id != -1 and channel_id != -1:
        raise InputError(
            description="Either channel_id or dm_id must be -1")

    if len(message) > 1000:
        raise InputError(
            description="Length of message cannot be more than 1000 characters")

    message_sent = 'New message: ' + message \
        + '\nOriginal message: ' + og_message

    share = True

    if dm_id == -1:
        shared_message_id = message_send_v1(
            token, ch_share[CH_ID_IDX], message_sent, share)

    if channel_id == -1:
        shared_message_id = message_senddm_v1(
            token, dm_share[DM_ID_IDX], message_sent, share)

    return {
        'shared_message_id': shared_message_id['message_id']
    }

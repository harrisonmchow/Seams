'''
dm.py:

This script contains functions which allow users to interact
with dms.

Functions:
    find_user(u_id)
    dm_create_v1(token, u_ids)
    dm_list_v1(token)
    dm_remove_v1(token, dm_id)
    dm_details_v1(token, dm_id)
    dm_leave_v1(token, dm_id)
    dm_messages_v1(auth_user_id, dm_id, start)
'''
import jwt

from src.data_store import data_store
from src.notifications import generate_notifcation
from src.data_store import U_PFP_IDX, data_store
from src.verify_session import verify_session
from src.data_store import U_ID_IDX, U_EMAIL_IDX, U_NAME_FIRST_IDX, U_NAME_LAST_IDX, U_HANDLE_IDX
from src.data_store import DM_ID_IDX, DM_OWN_IDX, DM_MEMBERS_IDX, DM_NAME_IDX
from src.error import InputError
from src.error import AccessError
from src.verify_session import verify_session
from src.other import check_dm_id
from datetime import datetime
from src.stats import update_dm_stats, update_workplace_dm_stats, update_workplace_msg_stats


SECRET = 'BADGER'


def find_user(u_id):
    '''
    Helper function for dm_create
    Retrieves the user info with a given u_id

    Arguments:
        u_id (int)      - user id of user

    Exception:
        ---

    Return Value:
        Returns user_info (list | u_id (int),
                                  email (str),
                                  first (str),
                                  last (str),
                                  handle (str))
    '''

    store = data_store.get()
    users = store['users']
    user_info = []

    for entry in users:
        if entry[U_ID_IDX] == u_id and u_id not in store['removed_users']:
            user_info.append(entry[U_ID_IDX])
            user_info.append(entry[U_EMAIL_IDX])
            user_info.append(entry[U_NAME_FIRST_IDX])
            user_info.append(entry[U_NAME_LAST_IDX])
            user_info.append(entry[U_HANDLE_IDX])
            user_info.append(entry[U_PFP_IDX])
            break

    return user_info


def dm_create_v1(token, u_ids):
    '''
    Creates a new direct message instance between users
    Takes in a valid token of the creator and a list of users to be included

    Arguments:
        token (str)
        u_ids (list | (int) )

    Exceptions:
        InputError - Occurs when:
            Inserted duplicate u_id
            Inserted invalid u_id

    Return Value:
        Returns: dm_id (dict | (int) )
    '''
    info_handle_idx = 4

    owner_id = verify_session(token)
    owner_info = find_user(owner_id)
    owner_dict = {'owner_info': owner_info, 'status': 'present', }

    store = data_store.get()
    dm_msg = []
    member_list = []
    handle_list = []

    # Generate the channel id
    new_dm_id = len(store['dms']) + 1

    # Add the creator of the channel to the list of owners and members

    owner = jwt.decode(token, SECRET, algorithms='HS256')
    owner_info = find_user(owner['auth_user_id'])
    owner_dict = {'owner_info': owner_info, 'status': 'present', }

    whole_user_list = u_ids
    whole_user_list.append(owner_dict['owner_info'][0])

    # Check for duplicates:
    if len(whole_user_list) != len(set(whole_user_list)):
        raise InputError(description='Duplicate u_id inserted')

    for u_id in u_ids:
        member_info = find_user(u_id)
        if not member_info:
            raise InputError(description='Invalid u_id inserted')
        else:
            member_list.append(member_info)
            handle_list.append(member_info[info_handle_idx])

    # Retrieves to alphabetical order and join
    handle_list.sort()
    dm_handle = ', '.join(handle_list)

    store['dms'].append(
        [new_dm_id, owner_dict, member_list, dm_handle, dm_msg])

    store['dm_messages'].append([])
    store['wordle_dm'].append({})
    data_store.set(store)

    data_store.set(store)
    store = data_store.get()
    for user in u_ids:
        if user != u_id:
            generate_notifcation(-1, new_dm_id, 3,
                                 owner_info[U_ID_IDX], user, dm_handle, -1)

    data_store.set(store)
    # Update dm stats for each user in the dm
    for user_id in whole_user_list:
        update_dm_stats(user_id, True)
    update_workplace_dm_stats(True)
    return {
        'dm_id': new_dm_id,
    }


def dm_list_v1(token):
    '''
    Display a list of DM that user is a member of

    Arguments:
        token (str)

    Exceptions:
        ---

    Return Values:
        Returns: dms ( list | {dict | (int), (name )} )
    '''
    store = data_store.get()
    user = {'auth_user_id': verify_session(token)}

    all_dms = []

    for dm in store['dms']:
        for member in dm[DM_MEMBERS_IDX]:
            if user['auth_user_id'] == member[0]:
                dm_info = {'dm_id': dm[DM_ID_IDX], 'name': dm[DM_NAME_IDX]}
                all_dms.append(dm_info)
                break

    return {
        'dms': all_dms,
    }


def dm_remove_v1(token, dm_id):
    '''
    Remove an existing DM, by removing all users and deleting the dm_id
    Can only be done by the creator of this DM

    Arguments:
        token (str)
        dm_id (int)

    Exceptions:
        InputError - Occurs when
            dm_id is not valid
        AccessError - Occurs when
            dm_id is valid but authorised user is not the creator of DM
            dm_id is valid but authorised user is no longer in the DM

    Return Values:
        NULL
    '''

    store = data_store.get()
    user = {'auth_user_id': verify_session(token)}

    dm_id_valid = False

    for dm in store['dms']:
        if dm[DM_ID_IDX] == dm_id:
            dm_id_valid = True
            if (user['auth_user_id'] != dm[DM_OWN_IDX]['owner_info'][0]):
                raise AccessError(
                    description='This user is either not authorised or has left the DM')
            elif (dm[DM_OWN_IDX]['status'] != 'present'):
                raise AccessError(
                    description='This user is either not authorised or has left the DM')
            # Delete this DM's users and owner
            dm[DM_OWN_IDX]['status'] = 'left'
            dm[DM_ID_IDX] -= 2 * dm_id
            # Update stats
            data_store.set(store)
            dm_m_id_idx = 0
            for user in dm[DM_MEMBERS_IDX]:
                id = user[dm_m_id_idx]
                update_dm_stats(id, False)

            # patch applied to dm_id to prevent it from being loaded
            store = data_store.get()
            dm[DM_MEMBERS_IDX].clear()
            break

    if dm_id_valid == False:
        raise InputError(description='Invalid dm_id inserted')

    # clear all the messages associated with the dm
    num_msgs = len(store['dm_messages'][dm_id])
    # clear the messages associated with the dm
    store['dm_messages'][dm_id].clear()
    data_store.set(store)
    # change stats about message and dm
    update_workplace_dm_stats(False)
    update_workplace_msg_stats(False, num_msgs)
    return {}


def dm_details_v1(token, dm_id):
    '''
    Returns the basic details (name and members) of this DM instance
    can only be done by the members by this DM

    Arguments:
        token (str)
        dm_id (int)

    Exceptions:
        InputError - Occurs when
            dm_id is not valid
        AccessError - Occurs when
            dm_id is valid but the authorised is not a member

    Return Values:
        name (str), members (list | (str) )
    '''

    store = data_store.get()
    user = {'auth_user_id': verify_session(token)}

    dm_name = ''
    member_list = []
    member_dict = []

    dm_id_valid = False

    for dm in store['dms']:
        if dm[DM_ID_IDX] == dm_id:
            dm_id_valid = True
            member_valid = False
            for member in dm[DM_MEMBERS_IDX]:
                if member[0] == user['auth_user_id']:
                    member_valid = True
                    break
            if member_valid == False:
                raise AccessError(
                    description='This user is either not a member or has left the DM')
            dm_name = dm[DM_NAME_IDX]
            for member in dm[DM_MEMBERS_IDX]:
                member_list.append(member)
            break

    if dm_id_valid == False:
        raise InputError(description='Invalid dm_id inserted')
    else:
        for member in member_list:
            print(member)
            member_dict.append({'u_id': member[0],
                                'email': member[1],
                                'name_first': member[2],
                                'name_last': member[3],
                                'handle_str': member[4],
                                'profile_img_url': member[5],
                                })

    return {
        'name': dm_name,
        'members': member_dict,
    }


def dm_leave_v1(token, dm_id):
    '''
    Users of this DM is removed as they leave
    Creator can leave and this instance will still exist
    Name of DM is not update if that occurs

    Arguments:
        token (str)
        dm_id (int)

    Exceptions:
        InputError - Occurs when
            dm_id does not refer to a valid DM
        AccessError - Occurs when
            dm_id is valid but authorised user is not a member of DM

    Return Values:
        NULL
    '''

    store = data_store.get()
    auth_user_id = verify_session(token)
    user = {'auth_user_id': auth_user_id}

    dm_owner_trig = False
    dm_member = []
    dm_id_valid = False

    for dm in store['dms']:
        if dm[DM_ID_IDX] == dm_id:
            dm_id_valid = True
            if (user['auth_user_id'] == dm[DM_OWN_IDX]['owner_info'][0]):
                if (dm[DM_OWN_IDX]['status'] == 'left'):
                    raise AccessError(
                        description='The owner has already left the DM')
                dm_owner_trig = True
                dm_member = dm[DM_OWN_IDX]['owner_info']
            else:
                member_valid = False
                for member in dm[DM_MEMBERS_IDX]:
                    if member[0] == user['auth_user_id']:
                        member_valid = True
                        dm_member = member
                        break
                if member_valid == False:
                    raise AccessError(
                        description='This user is either not a member or has left the DM')
            # Delete this DM's users or owner
            if dm_owner_trig == True:
                dm[DM_OWN_IDX]['status'] = 'left'
                dm[DM_MEMBERS_IDX].remove(dm_member)
            else:
                dm[DM_MEMBERS_IDX].remove(dm_member)

            break

    if dm_id_valid == False:
        raise InputError(description='Invalid dm_id inserted')
    data_store.set(store)
    update_dm_stats(auth_user_id, False)
    return {}


def dm_messages_v1(auth_user_id, dm_id, start):
    '''
    Takes an authenticated user id, an authenticated dm id which the user is a
    member of and a start value.  Returns up to 50 messages from most recent to least
    recent between index 'start' and 'start + 50'. If the least recent message is
    returned, -1 is returned in 'end' to indiciate no further messages are available.

    Arguments:
        auth_user_id (int) - A unique id which identifies each user
        dm_id (int) - A uniqe dm id which identifies each dm
        start (int) - The first message (in order of recency) the user would like to view

    Exceptions:
        AccessError - Occurs when dm_id is valid but the authorised user is not a member of the channel
        InputError - Occurs when dm_id does not refer to a valid dm
        InputError - Occurs when start is greater than the total number of messages in the channel

    Return Value:
        Returns dm messages (list of dictionaries), start(int), end(int)
    '''
    store = data_store.get()
    DM_MEM_ID_IDX = 0

   # Helper function to check if ID is valid
    dm = check_dm_id(dm_id)

    is_member = False
    for member in dm[DM_MEMBERS_IDX]:
        if member[DM_MEM_ID_IDX] == auth_user_id:
            is_member = True

    if is_member == False and auth_user_id:
        raise AccessError(description="You are not a member of this dm")

    total_messages = len(store['dm_messages'][dm_id])

    if total_messages == 0 and start > total_messages:
        raise InputError(
            description="There are no messages in this dm, start must be set to 0")

    if total_messages != 0 and start >= total_messages:
        raise InputError(
            description="You have set a start larger than the total number of messages")

    page_of_messages = []
    time_now = int(datetime.timestamp(datetime.now()))
    for idx, message in enumerate(reversed(store['dm_messages'][dm_id])):
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

    return {
        'messages': page_of_messages,
        'start': start,
        'end': end,
    }

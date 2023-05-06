'''
users.py:

This files contains functions which allow a user to
view other users, their stats or the users in a channel/dm.

Functions:
    users_all_v1()
    users_stats_v1(token)
    get_members_in_channel_or_dm()
'''
from src.data_store import CH_MEMBER_IDX, DM_MEMBERS_IDX, data_store, U_ID_IDX, U_EMAIL_IDX,\
    U_PFP_IDX, U_NAME_FIRST_IDX, U_NAME_LAST_IDX, U_HANDLE_IDX
from src.error import InputError
from src.error import AccessError
from src.message import check_message_send_later
from src.verify_session import verify_session


def users_all_v1():
    '''
    This function accesses the data store and returns a list of all users and their associated details.

    Arguments:
        N/A

    Exceptions:
        N/A

    Return Value:
        Returns users(list of dictionaries)
    '''
    store = data_store.get()

    # Covert the list of lists taken from data_stroe into a list of
    # dictionaries for the required output
    users = store['users'][:]
    removed = []
    for idx, user in enumerate(users):
        if user[U_ID_IDX] not in store['removed_users']:
            user_dict = {}
            user_dict['u_id'] = user[U_ID_IDX]
            user_dict['email'] = user[U_EMAIL_IDX]
            user_dict['name_first'] = user[U_NAME_FIRST_IDX]
            user_dict['name_last'] = user[U_NAME_LAST_IDX]
            user_dict['handle_str'] = user[U_HANDLE_IDX]
            user_dict['profile_img_url'] = user[U_PFP_IDX]
            users[idx] = user_dict
        else:
            removed.append(user)
    for rem_u in removed:
        users.remove(rem_u)

    return {"users": users}


def users_stats_v1(token):
    '''
    Description: 'users_stats_v1' is a function which returns a dictionary all users' 
        activity (the number of channels, dms and messages that exist)

        It verifies the token passed in within the list of sessions.

        then it creates a dictionary containing all user activity.

    Arguments:
        'token' - JWT token representing session ID

    Return Value:
        'workspace_stats' - A dictionary containing the stats of the user:
            'channels_exist': list of dictionaries
            'dms_exist': list of dictionaries
            'messages_exist': list of dictionaries
            'utilization_rate': float
    '''
    verify_session(token)
    check_message_send_later(token)

    data = users_all_v1()
    total_num_users = len(data['users'])
    users_in_ch_or_dm = get_members_in_channel_or_dm()
    store = data_store.get()
    channels_exist = store['channels_exist']
    dms_exist = store['dms_exist']
    messages_exist = store['messages_exist']

    # get utilization rate
    utilization_rate = users_in_ch_or_dm / total_num_users

    workplace_stats = {
        'channels_exist': channels_exist,
        'dms_exist': dms_exist,
        'messages_exist': messages_exist,
        'utilization_rate': utilization_rate,
    }

    return {
        'workspace_stats': workplace_stats
    }


def get_members_in_channel_or_dm():
    '''
    A helper function that looks through the datastore and gets the amount of users who are either in a dm or channel
    '''

    store = data_store.get()
    # a list of u_ids that are in at least 1 channel or dm
    in_ch_or_dm = []
    # go through all channels and append each user that is in a channel.
    # only count each member once, even if they are in multiple channels
    for channel in store['channels']:
        for user in channel[CH_MEMBER_IDX]:
            if user not in in_ch_or_dm:
                in_ch_or_dm.append(user)

    # go through all dms and append each user that is in a dm
    # don't repeat users, so if they are already in the list, don't append
    for dm in store['dms']:
        for user in dm[DM_MEMBERS_IDX]:
            if user[0] not in in_ch_or_dm:
                in_ch_or_dm.append(user[0])

    # the number of people in at least 1 channel or dm
    one_ch_or_dm = len(in_ch_or_dm)
    return one_ch_or_dm

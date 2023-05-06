'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''
import json
from src.error import AccessError
from os.path import exists
import os
# YOU SHOULD MODIFY THIS OBJECT BELOW
U_ID_IDX = 0
U_EMAIL_IDX = 1
U_PASSWORD_IDX = 2
U_NAME_FIRST_IDX = 3
U_NAME_LAST_IDX = 4
U_HANDLE_IDX = 5
U_PFP_IDX = 6
U_PW_RESET_CODE_IDX = 7
U_NOTIF_IDX = 8

CH_ID_IDX = 0
CH_NAME_IDX = 1
CH_SET_IDX = 2
CH_OWN_IDX = 3
CH_MEMBER_IDX = 4

SDUP_INIUSER_ID = 0
SDUP_CH_ID = 1
SDUP_T_END_ID = 2
SDUP_MSGS_ID = 3

M_ID_IDX = 0
M_U_ID_IDX = 1
M_MESSAGE_IDX = 2
M_TIME_IDX = 3
M_PINNED = 4

DM_ID_IDX = 0
DM_OWN_IDX = 1
DM_MEMBERS_IDX = 2
DM_NAME_IDX = 3
DM_MSG_IDX = 4
DM_MSG_PINNED = 4

initial_object = {
    # id, email, password, name_first, name_last, handle_str, reset_code, notifications
    'users': [],
    # u_id_idx = 0
    # u_email_idx = 1
    # u_password_idx = 2
    # u_name_first_idx = 3
    # u_name_last_idx = 4
    # u_handle_idx = 5
    # u_pfp idx = 6
    # u_pw_reset_code_idx = 7
    # u_notif_idx = 8
    'channels': [],     # ch_id, name_ch, public/private, owner members, all members TEST
    # ch_id_idx = 0
    # ch_name_idx = 1
    # ch_set_idx = 2
    # ch_own_idx = 3
    # ch_member_idx = 4
    'standups': [],
    # >standup: [[initiator_id, ch_id, time_finish, new_msg_id]]
    # SDUP_INIUSER_ID = 0
    # SDUP_CH_ID = 1
    # SDUP_T_END_ID = 2
    # SDUP_MSGS_ID = 3
    #   >new_msg_id
    #   !!! Deprecated !!! >SDUP_MSGS: [message_id1, message_id2, ...]
    'messages': [[]],
    # [none, ch1, ch2, ch3, ch4]
    #   >ch1 = [{'message_id': X, 'u_id': X, 'message': X, 'time_sent': X, 'is_pinned' : TRUE,
    #               'reacts':[{'react_id' : X, 'u_ids' : [X, X], 'is_this_user_reacted': True}, {} ]},
    #           {'message_id': X, 'u_id': X, 'message': X, 'time_sent': X, 'is_pinned' : TRUE,
    #               'reacts':[{'react_id' : X, 'u_ids' : [X, X], 'is_this_user_reacted': True}, {} ]}}]
    # Item 0 of 'messages' is empty beacuse channel_id's start with id 1

    'dm_messages': [[]],
    # [none, dm1, dm2, dm3, dm4]
    #   >dm1 = [{'message_id': X, 'u_id': X, 'message': X, 'time_sent': X, 'is_pinned' : TRUE},
    #           {'message_id': X, 'u_id': X, 'message': X, 'time_sent': X, 'is_pinned' : TRUE}]
    # Item 0 of 'messages' is empty
    # dm_m_id_idx = 0
    # dm_m_u_id_idx = 1
    # dm_m_message_idx = 2
    # dm_m_time_idx = 3
    # dm_m_pinned_idx = 4
    'messages_later': [],
    # contains the messages which should be sent later (dms and channels in same list)
    # each element in the form: {'channel' : True/False, 'location_id': (int), 'message_data': message_data}
    # 'channel' --> Whether the message is going to a channel or dm
    # 'location_id' --> channel_id or dm_id
    # 'message_data' --> {
    #   'message_id': message_id,
    #   'u_id': auth_id,
    #   'message': message,
    #   'time_sent': time_sent,
    #   'is_pinned': False,
    # }
    #   >dm1 = [{'message_id': X, 'u_id': X, 'message': X, 'time_sent': X, 'is_pinned' : TRUE,
    #               'reacts':[{'react_id' : X, 'u_ids' : [X, X], 'is_this_user_reacted': True}, {} ]},
    #           {'message_id': X, 'u_id': X, 'message': X, 'time_sent': X, 'is_pinned' : TRUE,
    #               'reacts':[{'react_id' : X, 'u_ids' : [X, X], 'is_this_user_reacted': True}, {} ]}}]
    # Item 0 of 'dm_messages' is empty beacuse dm_id's start with id 1

    'dms': [],
    # dm_id (int), owner (dict), members (list), name (str), msg (list of dict)
    #   > msg (list of dict) -> {'msg_id': (int), 'message': (str), 'time_sent': X }
    # dm_id_idx = 0
    #   > dm_id : a single (int)
    # NOTE: dm_id starts at 1, there are no function-created dm_id that starts at 0
    # dm_own_idx = 1
    #   > a dictionary of structure: {'owner_info': (list) containing u_id, email, first/last, handler IN ORDER,
    #                                 'status': (str) containing either 'present' or 'leave',}
    # dm_members_idx = 2
    #   > a list of members (list of lists) i.e.:
    #   [[1, 'felix.li@vtub.er', 'felix', 'li', 'felixli'],
    #    [u_id (int), email (str), first (str), last (str), handle (str)]]
    # dm_name_idx = 3
    #   > a str of alphabetically sorted member name handlers seperated by comma-and-space
    # dm_msg_idx = 4
    #   > a list of dictionary containing msg_id and message i.e.:
    #   [{'msg_id': 1, 'msg': 'hello', 'u_id': 1},
    #    {'msg_id': 2, 'msg': 'hi there', 'u_id': 2}]

    'message_counter': 0,
    'register_counter': 0,

    'global_owner': [],
    'removed_users': [],
    'removed_emails': [],
    'removed_handles': [],
    'sessions': [],
    'channel_track': [],
    # each element in the form --> {auth_user_id: int, channels_joined: [{num_channels_joined: int, time_stamp: int}, ect]}
    'dm_track': [],
    # each element in the form --> {auth_user_id: int, dms_joined: [{num_dms_joined: int, time_stamp: int}, ect]}
    'message_track': [],
    # each element in the form --> {auth_user_id: int, messages_sent: [{num_messages_sent: int, time_stamp: int}, ect]}
    'channels_exist': [],
    # each element in the form --> {num_channels_exist: int, time_stamp: int}
    'dms_exist': [],
    # each element in the form --> {num_dms_exist: int, time_stamp: int}
    'messages_exist': [],
    # each element in the form --> {num_messages_exist: int, time_stamp: int}
    'valid_reacts': [1],
    'wordle_ch': [[]],
    'wordle_dm': [[]],
}


class Datastore:
    '''
    Data store object that handles the data access between backend and database
    member function:
        __init__()
        get()
        set()
    '''

    def __init__(self):
        '''initialize data_store'''

        if exists('src/data_store.json'):  # file exist

            if os.stat("src/data_store.json").st_size == 0:  # file empty
                self.__store = initial_object
                with open('src/data_store.json', 'w', encoding="utf8") as file:
                    json.dump(self.__store, file)
            else:  # load from file if not empyt and exists
                with open('src/data_store.json', 'r', encoding="utf8") as file:
                    file_contents = json.load(file)
                    self.__store = file_contents
        # else initialise it
        else:
            self.__store = initial_object
            with open('src/data_store.json', 'w', encoding="utf8") as file:
                json.dump(self.__store, file)

    def get(self):
        '''call data_store object to get database'''

        with open('src/data_store.json', 'r', encoding="utf8") as file:
            file_contents = json.load(file)

        if file_contents != self.__store:
            raise AccessError(description="DATA STORE NOT SYNCED")

        return self.__store

    def set(self, store):
        '''set data store to a given state'''
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')

        with open('src/data_store.json', 'w', encoding="utf8") as file:
            json.dump(store, file)

        self.__store = store

        return True


print('Loading Datastore...')

global data_store
data_store = Datastore()

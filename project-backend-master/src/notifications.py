'''
This module adds the notification functionaility and is responsible for store and creating new
notifications. A notification is generated in any of the three following cases;
    - A user is tagged 
    - A user reacts to a message
    - A user is invited to a channel/dm
'''


from src.data_store import U_HANDLE_IDX, U_ID_IDX, U_NOTIF_IDX, data_store
from src.verify_session import verify_session

# case is an indicator for one of the 3 types of notifications


def find_user(auth_user_id):
    '''
    Description: Find user is a helper function designed to take in a u_id and return the user associated with 
    it.

    Arguments:
        'auth_user_id'    (int) - An integer representing a user's id.

    Exceptions:
        InputError - Occurs when the auth_user_id cannot be found in datastore.

    Return Value:
        Returns 'user' (A list in datastore containing all the user information) if the u_id is found in data store.
    '''
    store = data_store.get()
    user_found = None
    for user in store['users']:
        if user[U_ID_IDX] == auth_user_id:
            user_found = user
    return user_found


def channeldm_invite_notif(invitor_id, invitee_id, ch_or_dm_name, notification):
    store = data_store.get()
    invitor = find_user(invitor_id)
    invitee = find_user(invitee_id)
    notification['notification_message'] = f"{invitor[U_HANDLE_IDX]} added you to {ch_or_dm_name}"
    invitee[U_NOTIF_IDX].append(notification)
    data_store.set(store)


def react_notification(invitor_id, invitee_id, ch_or_dm_name, notification):
    store = data_store.get()
    invitor = find_user(invitor_id)
    invitee = find_user(invitee_id)

    notification['notification_message'] = f"{invitor[U_HANDLE_IDX]} reacted to your message in {ch_or_dm_name}"
    invitee[U_NOTIF_IDX].append(notification)

    data_store.set(store)


def tagging_notifcation(tagger_id, tagged_id, ch_or_dm_name, message, notification):
    store = data_store.get()
    tagger = find_user(tagger_id)
    tagged = find_user(tagged_id)
    message_20 = message[:20]

    notification['notification_message'] = f"{tagger[U_HANDLE_IDX]} tagged you in {ch_or_dm_name}: {message_20}"

    tagged[U_NOTIF_IDX].append(notification)
    data_store.set(store)


def generate_notifcation(channel_id, dm_id, case, invitor_id, invitee_id, ch_or_dm_name, message):
    # dm message
    store = data_store.get()
    if channel_id == -1:
        notification = {'channel_id': -1, 'dm_id': dm_id,
                        'notification_message': message}
        if case == 1:
            tagging_notifcation(invitor_id, invitee_id,
                                ch_or_dm_name, message, notification)
        elif case == 2:
            react_notification(invitor_id, invitee_id,
                               ch_or_dm_name, notification)
        elif case == 3:
            channeldm_invite_notif(
                invitor_id, invitee_id, ch_or_dm_name, notification)

    if dm_id == -1:
        notification = {'channel_id': channel_id,
                        'dm_id': -1, 'notification_message': message}
        if case == 1:
            tagging_notifcation(invitor_id, invitee_id,
                                ch_or_dm_name, message, notification)
        elif case == 2:
            react_notification(invitor_id, invitee_id,
                               ch_or_dm_name, notification)
        elif case == 3:
            channeldm_invite_notif(
                invitor_id, invitee_id, ch_or_dm_name, notification)

    data_store.set(store)


def get_notifications(token):
    auth_user_id = verify_session(token)
    store = data_store.get()

    notif = None
    for user in store['users']:
        if user[U_ID_IDX] == auth_user_id:
            if len(user[U_NOTIF_IDX]) > 20:
                notif = {'notifications': user[U_NOTIF_IDX][-20:]}
            else:
                notif = {'notifications': user[U_NOTIF_IDX]}
    return notif

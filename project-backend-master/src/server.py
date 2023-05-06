from email.mime import image
import sys
import os.path
import signal
from json import dumps
from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS
from src.channels import channels_create_v1, channels_list_v1, channels_listall_v1

# from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1, message_pin_unpin, message_sendlater_v1, message_sendlaterdm_v1, check_message_send_later
from src.message import message_send_v1, message_edit_v1, message_remove_v1, \
    message_senddm_v1, message_pin_unpin, message_sendlater_v1, \
    message_sendlaterdm_v1, message_react_unreact_v1, message_share_v1, check_message_send_later
from src.error import InputError
from src import config
from src.channel import channel_invite_v1, channel_join_v1, channel_details_v1, \
    channel_messages_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.channels import channels_create_v1
from src.notifications import get_notifications
# from src.user import user_set_handle, change_userpermission, user_profile_setname_v1, user_profile_setemail_v1, remove_user_v1, user_profile_v1, user_stats_v1
from src.user import user_set_handle, change_userpermission, user_profile_setname_v1, user_profile_setemail_v1, remove_user_v1, user_profile_v1, upload_pic, user_stats_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.search import search_v1
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
# , remove_user_v1
from PIL import Image
from src.other import clear_v1
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1, password_reset_request_v1, password_reset_reset_v1
from flask import jsonify
from src.verify_session import verify_session
from src.users import users_all_v1, users_stats_v1
from src.extra import check_wordle


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)
# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example


@APP.route("/echo", methods=['GET'])
def echo2():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    #ret = echo(data)
    return dumps({
        'data': data
    })


@APP.route("/imgurl/<URL>", methods=['GET'])
def get_pfp(URL):
    return send_from_directory('./pfps', URL)


@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def pfp():
    '''
    Converts http data to parameters which are then
    passed into upload_pic().

    Return Value:
        Returns {}
    '''
    data = request.get_json()
    token = data['token']
    img_url = data['img_url']
    x_start = data['x_start']
    y_start = data['y_start']
    x_end = data['x_end']
    y_end = data['y_end']
    upload_pic(token, img_url, x_start, y_start, x_end, y_end)
    return dumps({})


@APP.route("/message/pin/v1", methods=['POST'])
def pin():
    '''
    Converts http data to parameters which are then
    passed into check_message_send_later().

    Return Value:
        Returns {}
    '''
    data = request.get_json()
    token = data['token']
    mid = data['message_id']
    check_message_send_later(token)
    message_pin_unpin(token, mid, True)
    return dumps({})


@APP.route("/message/unpin/v1", methods=['POST'])
def unpin():
    '''
    Converts http data to parameters which are then
    passed into check_message_send_later().

    Return Value:
        Returns {}
    '''
    data = request.get_json()
    token = data['token']
    mid = data['message_id']
    check_message_send_later(token)
    message_pin_unpin(token, mid, False)
    return dumps({})


@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    '''
    Converts http data to parameters which are then
    passed into channels_create_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns channel_id(int)
    '''
    data = request.get_json()
    name = data['name']
    is_public = data['is_public']
    token = data['token']
    auth_user_id = verify_session(token)
    return dumps(channels_create_v1(auth_user_id, name, is_public))


@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    '''
    Converts http data to parameters which are then
    passed into channels_list_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns channels(list of dictionaries)
    '''
    token = request.args.get('token')
    auth_user_id = verify_session(token)
    return dumps(channels_list_v1(auth_user_id))


@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    '''
    Converts http data to parameters which are then
    passed into channels_listall_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns channels(list of dictionaries)
    '''
    token = request.args.get('token')
    auth_user_id = verify_session(token)
    return dumps(channels_listall_v1(auth_user_id))


@APP.route("/message/send/v1", methods=['POST'])
def message_send_v1_front():
    '''
    Converts http data to parameters which are then
    passed into message_send_v1().

    Return Value:
        Returns message_id(int)
    '''
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    share = False
    check_message_send_later(token)
    ret = check_wordle(token, channel_id, message, 0, share)
    if ret == True:
        return dumps({})
    else:
        return dumps(message_send_v1(token, channel_id, message, share))
    # return dumps(message_send_v1(token, channel_id, message, share))


@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v1_front():
    '''
    Converts http data to parameters which are then
    passed into message_edit_v1().

    Return Value:
        Null
    '''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message = data['message']
    check_message_send_later(token)
    return dumps(message_edit_v1(token, message_id, message))


@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1_front():
    '''
    Converts http data to parameters which are then
    passed into message_remove_v1().

    Return Value:
        Null
    '''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    check_message_send_later(token)
    return dumps(message_remove_v1(token, message_id))


@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_v1_front():
    '''
    Converts http data to parameters which are then
    passed into message_senddm_v1().

    Return Value:
        Returns message_id(int)
    '''
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    message = data['message']
    share = False
    check_message_send_later(token)
    ret = check_wordle(token, dm_id, message, 1, share)
    if ret == True:
        return dumps({})
    else:
        return dumps(message_senddm_v1(token, dm_id, message, share))
    # return dumps(message_senddm_v1(token, dm_id, message, share))


@APP.route('/clear/v1', methods=['DELETE'])
def clear_v2():
    return dumps(clear_v1())


@APP.route('/auth/register/v2', methods=['POST'])
def server_auth_register_v2():
    '''
    Converts http data to parameters which are then
    passed into auth_register_v2().

    Return Value:
        Returns {token, auth_user_id}
    '''
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']
    first = request_data['name_first']
    last = request_data['name_last']
    return dumps(auth_register_v2(email, password, first, last))


@APP.route('/auth/login/v2', methods=['POST'])
def server_auth_login_v2():
    '''
    Converts http data to parameters which are then
    passed into auth_login_v2().

    Return Value:
        Returns {token, auth_user_id}
    '''
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']
    return dumps(auth_login_v2(email, password))


@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2():
    '''
    Converts http data to parameters which are then
    passed into channel_messages_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns messages(list of dictionaries), start(int), end(int)
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    check_message_send_later(token)
    auth_user_id = verify_session(token)
    return dumps(channel_messages_v1(auth_user_id, channel_id, start))


@APP.route("/channel/leave/v1", methods=['POST'])
def http_channel_leave_v1():
    '''
    Converts http data to parameters which are then
    passed into channel_leave_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    auth_user_id = verify_session(token)
    return dumps(channel_leave_v1(auth_user_id, channel_id))


@APP.route('/channel/invite/v2', methods=['POST'])
def http_channel_invite():
    '''
    Converts http data to parameters which are then
    passed into channel_invite_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    ch_id = request_data['channel_id']
    u_id = request_data['u_id']
    auth_user_id = verify_session(token)
    return dumps(channel_invite_v1(auth_user_id, ch_id, u_id))


@APP.route('/channel/join/v2', methods=['POST'])
def http_channel_join():
    '''
    Converts http data to parameters which are then
    passed into channel_join_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    ch_id = request_data['channel_id']
    auth_user_id = verify_session(token)
    return dumps(channel_join_v1(auth_user_id, ch_id))


@APP.route('/channel/details/v2', methods=['GET'])
def http_channel_details():
    '''
    Converts http data to parameters which are then
    passed into channel_details_v1().

    Return Value:
        Returns {name, is_public, owner_members, all_members}
    '''
    token = request.args.get('token')
    ch_id = int(request.args.get('channel_id'))
    auth_user_id = verify_session(token)
    return dumps(channel_details_v1(auth_user_id, ch_id))


@APP.route('/channel/addowner/v1', methods=['POST'])
def http_channel_addowner():
    '''
    Channel addowner server call
    Passes a jwt, channel id and user id to the function
    Error: Returns 400/403
    '''
    request_data = request.get_json()
    token = request_data['token']
    ch_id = request_data['channel_id']
    u_id = request_data['u_id']
    return dumps(channel_addowner_v1(token, ch_id, u_id))


@APP.route('/channel/removeowner/v1', methods=['POST'])
def http_channel_removeowner():
    '''
    Channel removeowner server call
    Passes a jwt, channel id and user id to the function
    Error: Returns 400/403
    '''
    request_data = request.get_json()
    token = request_data['token']
    ch_id = request_data['channel_id']
    u_id = request_data['u_id']
    return dumps(channel_removeowner_v1(token, ch_id, u_id))


@APP.route('/dm/create/v1', methods=['POST'])
def http_dm_create():
    '''
    DM create server call
    Passes a jwt, and a list of user ids to the function
    Error: Returns 400
    '''
    request_data = request.get_json()
    token = request_data['token']
    u_ids = request_data['u_ids']
    return dumps(dm_create_v1(token, u_ids))


@APP.route('/dm/list/v1', methods=['GET'])
def http_dm_list():
    '''
    DM list server call
    Passes a jwt to the function
    '''
    token = request.args.get('token')
    return dumps(dm_list_v1(token))


@APP.route('/dm/remove/v1', methods=['DELETE'])
def http_dm_remove():
    '''
    DM remove server call
    Passes a jwt, and a dm_id to the function
    Error: Returns 400/403
    '''
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    return dumps(dm_remove_v1(token, dm_id))


@APP.route('/dm/details/v1', methods=['GET'])
def http_dm_details():
    '''
    DM details server call
    Passes a jwt, and a dm_id to the function
    Error: Returns 400/403
    '''
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    return dumps(dm_details_v1(token, dm_id))


@APP.route('/dm/leave/v1', methods=['POST'])
def http_dm_leave():
    '''
    DM leave server call
    Passes a jwt, and a dm_id to the function
    Error: Returns 400/403
    '''
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    return dumps(dm_leave_v1(token, dm_id))


@APP.route("/dm/messages/v1", methods=['GET'])
def http_dm_messages_v1():
    '''
    Converts http data to parameters which are then
    passed into dm_messages_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns dm messages (list of dictionaries), start(int), end(int)
    '''
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    check_message_send_later(token)
    auth_user_id = verify_session(token)
    return dumps(dm_messages_v1(auth_user_id, dm_id, start))


@APP.route('/search/v1', methods=['GET'])
def http_search_v1():
    '''
    Intermediates the input to search_v1 from client-server calls
    Passes a jwt and a query string

    Return: a list of messages containing the query
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    check_message_send_later(token)
    return dumps(search_v1(token, query_str))


@APP.route('/standup/start/v1', methods=['POST'])
def http_standup_start():
    '''
    Intermediates the input to standup_start_v1 from client-server calls
    Passes a jwt of a user (str), a channel id (int), and a length (int)

    Return: the time which the standup is projected to finish
    '''
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    length = request_data['length']

    return dumps(standup_start_v1(token, channel_id, length))


@APP.route('/standup/active/v1', methods=['GET'])
def http_standup_active():
    '''
    Intermediates the input to standup_start_v1 from client-server calls
    Passes a jwt of a user (str), a channel id (int)

    Return: the time which the standup is projected to finish,
            and `None` if a standup is not running
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(standup_active_v1(token, channel_id))


@APP.route('/standup/send/v1', methods=['POST'])
def http_standup_send():
    '''
    Intermediates the input to standup_send_v1 from client-server calls
    Passes a jwt of a user (str), a channel id (int), and a message (str)

    Return Value:
     Returns {time_finish}
    '''
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']

    return dumps(standup_send_v1(token, channel_id, message))


@APP.route('/user/profile/sethandle/v1', methods=['PUT'])
def http_sethandle():
    '''
    Converts http data to parameters which are then
    passed into user_set_handle().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    handle_str = request_data['handle_str']
    auth_user_id = verify_session(token)
    return dumps(user_set_handle(auth_user_id, handle_str))


@APP.route('/user/profile/setname/v1', methods=['PUT'])
def http_user_profile_setname():
    '''
    Converts http data to parameters which are then
    passed into user_profile_setname_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns an empty dictionary
    '''
    request_data = request.get_json()
    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']
    auth_user_id = verify_session(token)
    return dumps(user_profile_setname_v1(auth_user_id, name_first, name_last))


@APP.route('/user/profile/setemail/v1', methods=['PUT'])
def http_user_profile_setemail():
    '''
    Converts http data to parameters which are then
    passed into user_profile_setemail_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    email = request_data['email']
    auth_user_id = verify_session(token)
    return dumps(user_profile_setemail_v1(auth_user_id, email))


@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def http_change_perms():
    '''
    Converts http data to parameters which are then
    passed into change_userpermission().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    p_id = request_data['permission_id']
    auth_user_id = verify_session(token)
    return dumps(change_userpermission(auth_user_id, u_id, p_id))


@APP.route('/users/all/v1', methods=['GET'])
def http_users_all_v1():
    '''
    Converts http data to parameters which are then
    passed into users_all_v1().Also uses 
    verify_session() to verify the provided token
    and switches it for the relevent auth_user_id.

    Return Value:
        Returns users(list of dictionaries)
    '''
    token = request.args.get('token')
    verify_session(token)
    return dumps(users_all_v1())


@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def http_remove_user():
    '''
    Converts http data to parameters which are then
    passed into remove_user_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    auth_user_id = verify_session(token)
    return dumps(remove_user_v1(auth_user_id, u_id))


@APP.route('/user/profile/v1', methods=['GET'])
def http_user_profile_v1():
    '''
    Converts http data to parameters which are then
    passed into user_profile_v1().

    Return Value:
        Returns {user}
    '''
    token = request.args.get('token')
    user_id = int(request.args.get('u_id'))
    return dumps(user_profile_v1(user_id, token))


@APP.route('/auth/logout/v1', methods=['POST'])
def server_auth_logout_v1():
    '''
    Converts http data to parameters which are then
    passed into auth_logout_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    token = request_data['token']
    return dumps(auth_logout_v1(token))


@APP.route('/auth/passwordreset/request/v1', methods=['POST'])
def server_auth_password_reset_request_v1():
    '''
    Converts http data to parameters which are then
    passed into password_reset_request_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    email = request_data['email']
    return dumps(password_reset_request_v1(email))


@APP.route('/auth/passwordreset/reset/v1', methods=['POST'])
def server_auth_password_reset_reset_v1():
    '''
    Converts http data to parameters which are then
    passed into password_reset_reset_v1().

    Return Value:
        Returns {}
    '''
    request_data = request.get_json()
    reset_code = request_data['reset_code']
    new_password = request_data['new_password']
    return dumps(password_reset_reset_v1(new_password, reset_code))


@APP.route('/message/sendlater/v1', methods=['POST'])
def server_message_sendlater_v1():
    '''
    Converts http data to parameters which are then
    passed into message_sendlater_v1().

    Return Value:
        Returns a message id (int)
    '''
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    time_sent = data['time_sent']
    return dumps(message_sendlater_v1(token, channel_id, message, time_sent))


@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def server_message_sendlaterdm_v1():
    '''
    Converts http data to parameters which are then
    passed into message_sendlater_v1().

    Return Value:
        Returns a message id (int)
    '''
    data = request.get_json()
    token = data['token']
    dm_id = data['dm_id']
    message = data['message']
    time_sent = data['time_sent']
    return dumps(message_sendlaterdm_v1(token, dm_id, message, time_sent))


@APP.route('/user/stats/v1', methods=['GET'])
def server_user_stats_v1():
    '''
    Converts http data to parameters which are then
    passed into user_stats_v1().

    Return Value:
        Returns a dictionary containing user_stats
    '''
    token = request.args.get('token')
    return dumps(user_stats_v1(token))


@APP.route('/users/stats/v1', methods=['GET'])
def server_users_stats_v1():
    '''
    Converts http data to parameters which are then
    passed into users_stats_v1().

    Return Value:
        Returns a dictionary containing user_stats
    '''
    token = request.args.get('token')
    return dumps(users_stats_v1(token))


@APP.route('/message/react/v1', methods=['POST'])
def server_message_react_v1():
    '''
    Converts http data to parameters which are then
    passed into message_react_unreact_v1().

    Return Value:
        Returns {}
    '''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    react_id = data['react_id']
    unreact = False
    return dumps(message_react_unreact_v1(token, message_id, react_id, unreact))


@APP.route('/message/unreact/v1', methods=['POST'])
def server_message_unreact_v1():
    '''
    Converts http data to parameters which are then
    passed into message_react_unreact_v1().

    Return Value:
        Returns {}
    '''
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    react_id = data['react_id']
    unreact = True
    return dumps(message_react_unreact_v1(token, message_id, react_id, unreact))


@APP.route('/notifications/get/v1', methods=['GET'])
def server_notification_get_v1():
    '''
    Converts http data to parameters which are then
    passed into get_notifications_v1().
    Return Value:
        Returns {}
    '''
    token = request.args.get('token')
    return dumps(get_notifications(token))


@APP.route('/message/share/v1', methods=['POST'])
def server_message_share_v1():
    '''
    Converts http data to parameters which are then
    passed into message_share_v1().

    Return Value:
        Returns {shared_message_id}
    '''
    data = request.get_json()
    token = data['token']
    og_message_id = data['og_message_id']
    message = data['message']
    channel_id = data['channel_id']
    dm_id = data['dm_id']
    return dumps(message_share_v1(token, og_message_id, message, channel_id, dm_id))


# NO NEED TO MODIFY BELOW THIS POINT
if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    # Do not edit this port  #############added debug
    # APP.run(port=config.port, debug=True)
    APP.run(port=config.port)

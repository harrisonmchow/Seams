'''
auth.py:

This script allows the user to either create a new account or login to their previously registered
account. It is responsible for verifying user details, creating a unique 'auth_user_id', 'handle'
and json web token and storing the necessary information in data_store. 

Functions:
    auth_login_v1 (email, password)
    create_token (auth_user_id)
    create_handle (name_first, name_last)
    auth_logout (token)
    auth_register_v1 (email, password, name_first, name_last)
'''
from datetime import datetime, timedelta
import re
import jwt
import uuid
import smtplib
import random
import time
import hashlib
from email.message import EmailMessage
from src.data_store import U_NAME_FIRST_IDX, U_NAME_LAST_IDX, data_store
from src.data_store import U_EMAIL_IDX, U_PASSWORD_IDX, U_ID_IDX, U_HANDLE_IDX, U_PW_RESET_CODE_IDX
from src.error import InputError, AccessError
from datetime import datetime
from src.config import url as URL


def auth_login_v2(email, password):
    '''
    Description: auth_login_v2 logs a user into the system provided they can input a registered
        email and the password associated with it. If successful, auth_login_v2 returns a 
        dictionary containing the user_id and token of that registered account.

    Arguments:
        'email' - A string of characters representing the email address input by the user
        'password' - A string of characters representing the password input by the user

    Exceptions:
        InputError - Occurs when the email given is not present within the system
        InputError - Occurs when the password given doesn't match the password for that email

    Return Value:
        Dictionary {'auth_user_id': <int>, 'token': <str>} 
    '''
    store = data_store.get()
    # Validate email
    email_found = False
    for user in store['users']:
        if user[U_EMAIL_IDX] == email:
            email_found = True
            found_user = user

    if email_found is False:
        raise InputError(description="User not found")

    hash_object = hashlib.sha1(password.encode())
    password_encrypted = hash_object.hexdigest()

    if password_encrypted != found_user[U_PASSWORD_IDX]:
        raise InputError(description="Incorrect Password")

    # Generate a jwt token which can represent the user's session
    user_token = create_token(found_user[U_ID_IDX])

    # Store the token into the list of current session's
    store['sessions'].append(user_token)
    data_store.set(store)

    return ({'auth_user_id': found_user[U_ID_IDX],  'token': user_token})


def create_handle(name_first, name_last):
    '''
    Description: 'create_handle' is a helper function to 'auth_register_v2' and is designed to
        create a unique handle for each user.

        It combines the user's first and last name into a concatenated all-lowercase string which 
        is then searched for in data_store to ensure there are no duplicates.

        If a duplicate is found, an integer corresponding to the number of prior duplicates
        is added to that handle

        e.g. 'gerardmathews', 'gerardmathews0', 'gerardmathews1' etc.

    Arguments:
        'name_first' (string) - An alphabetic string containing the user's first name.
        'name_last'  (string)-  An alphabetic string containing the user's last name.

    Assumption: Assume that parameters are valid names because they were already
        validated by auth_register_v2.

    Return Value:
        'handle_str' - A unique string generated from the user's first and last name.
    '''
    store = data_store.get()

    handle_str = name_first.strip() + name_last.strip()
    handle_str = handle_str[0:20]
    handle_str = handle_str.lower()
    handle_str_alphabetic = re.compile("[^a-zA-Z]")
    handle_str = re.sub(handle_str_alphabetic, "", handle_str)
    num_duplicates = 0

    # Convert the handle into a string of entirely lower case alphabetic charaters.
    handle_str = handle_str.lower()
    handle_str_alphabetic = re.compile("[^a-zA-Z]")
    handle_str = re.sub(handle_str_alphabetic, "", handle_str)

    num_duplicates = 0
    handle_str = handle_str[0:20]

    for user in store['users']:
        handle = user[U_HANDLE_IDX]

        handle = handle[0:20]

        # Removes any numbers from the handle
        handle = re.sub(r'[0-9]+', '', handle)
        if handle == handle_str:
            num_duplicates += 1
        # Matched but user has been removed so register will reuse that handle
        if handle == handle_str and handle in store['removed_handles']:
            store['removed_handles'].remove(handle)
            handle_str = handle
            return handle_str

    if num_duplicates > 0:
        handle_str += str(num_duplicates - 1)

    return handle_str


def create_token(auth_user_id):
    '''
    Description: 'create_token' is a helper function to 'auth_login_v2' and 'auth_register_v2'. It
        is designed to create a json web token containing the user's auth_user_id each time they 
        login into the system.

    Arguments:
        'auth_user_id'    (dictionary) - A dictionary containing the users id.

    Return Value:
        'user_token' - An encoded json web token containing the user's auth_user_id.
    '''
    # To make each jwt unique, the payload contain a universal unique indetifiers
    id = str(uuid.uuid4())

    user_token = jwt.encode(
        payload={"auth_user_id": auth_user_id, "uuid": id}, key="BADGER")
    return user_token


def auth_register_v2(email, password, name_first, name_last):
    '''
    Description: auth_register_v2 registers a new user in data_store.
        auth_register_v2:

        - Verifies if the user's details are valid

        - Searches data_store to see if the email is already registered in the system

        - Creates a unique handle string for the user by calling 'create_handle'

        - Encodes the password using sha256_crypt

        - Allocates a unique user id

        - Creates a json web token containing the 'auth_user_id'

        - Stores the user's details (id, email, first name, last name, password, handle)

    Arguments:
        'email'    (string) - A string of characters representing the email address from user input
        'password' (string) - A string of characters representing the password input by the user
        'name_first' (string) - An alphabetic string containing the user's first name.
        'name_last'  (stirng) - An alphabetic string containing the user's last name.

    Exceptions:
        InputError - Occurs when the given email is not in a valid format
        InputError - Occurs when password is less than 6 characters
        InputError - Occurs when name_first is not between 1 and 50 characters
        InputError - Occurs when name_last is not between 1 and 50 characters
        InputError - Occurs when the given email is already registered

    Return Value:
        Dictionary {'auth_user_id': <int>} representing unique ID of the user
    '''
    store = data_store.get()

    # Specified email format
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    match = re.fullmatch(regex, email)
    if match is None:
        raise InputError(description="Invalid email format")

    if len(password) < 6:
        raise InputError(
            description="Password length must be longer than 6 characters")

    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError(
            description="First name must be between 1 and 50 characters")

    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError(
            description="Last name must be between 1 and 50 characters")

    for user in store['users']:
        if user[U_EMAIL_IDX] == email and (email not in store['removed_emails']):
            raise InputError(description="Email already in use")
        elif user[U_EMAIL_IDX] == email and (email in store['removed_emails']):
            store['removed_emails'].remove(email)

    #Password is hashed
    # password_encrypted = pbkdf2_sha256.encrypt(password)
    data_store.set(store)

    hash_object = hashlib.sha1(password.encode())
    password_encrypted = hash_object.hexdigest()
    print(password_encrypted)
    data_store.set(store)

    handle_str = create_handle(name_first, name_last)

    new_id = store['register_counter'] + 1
    store['register_counter'] = new_id
    # Global permission
    time_now = int(datetime.timestamp(datetime.now()))
    if store['register_counter'] == 1:
        store['global_owner'].append(new_id)
        # If its the first user, start tracking workplace stats
        workplace_ch = {'num_channels_exist': 0, 'time_stamp': time_now}
        workplace_dm = {'num_dms_exist': 0, 'time_stamp': time_now}
        workplace_msg = {'num_messages_exist': 0, 'time_stamp': time_now}
        store['channels_exist'].append(workplace_ch)
        store['dms_exist'].append(workplace_dm)
        store['messages_exist'].append(workplace_msg)

    # intial reset code for all users
    reset_code = {'reset_code': 0, 'expiry_date': time.mktime(
        datetime.now().timetuple())}

    user_notifications = []

    default_img = f"{URL}/imgurl/0.jpg"
    store['users'].append(
        [new_id, email, password_encrypted, name_first, name_last, handle_str, default_img, reset_code, user_notifications])

    # keep track of the users channels, dms and messages

    channels = {'auth_user_id': new_id, 'channels_joined': [
        {'num_channels_joined': 0, 'time_stamp': time_now}]}
    dms = {'auth_user_id': new_id, 'dms_joined': [
        {'num_dms_joined': 0, 'time_stamp': time_now}]}
    msgs = {'auth_user_id': new_id, 'messages_sent': [
        {'num_messages_sent': 0, 'time_stamp': time_now}]}

    store['channel_track'].append(channels)
    store['dm_track'].append(dms)
    store['message_track'].append(msgs)

    data_store.set(store)

    user_token = auth_login_v2(email, password)['token']
    return ({'auth_user_id': new_id, 'token': user_token})


def auth_logout_v1(token):
    '''
    Description: 'auth_logout_v1' is designed to invalidate an already validated json web token (JWT).
        The function will only make one JWT invalid at a time, this means that a user with multiple
        valid JWT's can continue using their other JWT's as valid tokens.

    Arguments:
        'token' - JWT token representing session ID

    Exceptions:
        AccessError - Occurs when the token cannot be found in the list of sessions

    Return Value:
        {} - Returns empty dictionary
    '''
    store = data_store.get()

    # Search the sessions list for the specified token. If found, remove that entry from the list
    found_session = False
    for idx, session in enumerate(store['sessions']):
        if session == token:
            found_session = True
            del store['sessions'][idx]

    if not found_session:
        raise AccessError(description="Unknown Session")
    else:
        data_store.set(store)
    return {}

#
# Request a password reset
#


def password_reset_request_v1(email):
    '''
    Description: 'password_reset_request_v1' is the first half of the password reset functionality and
        is designed to send an automated email for the user to change their password. This emails 
        contains a url and secret code to verify the password change. It takes in the email of the
        user making the passwor dchange and searches to find if they are a vlid and registered user.

    Arguments:
        'email' - A string representing A Users email address

    Return Value:
        {} - Returns empty dictionary
    '''
    store = data_store.get()
    # search for email in data store
    email_found = False
    for user in store['users']:
        if user[U_EMAIL_IDX] == email:
            email_found = True
            found_user = user

    if email_found:
        # generate secret code
        secret_code = random.randint(100000, 999999)
        # store this code in data store so that it can be verified
        expiry_time = datetime.now() + timedelta(days=1)
        expiry_time = time.mktime(expiry_time.timetuple())
        found_user[U_PW_RESET_CODE_IDX] = {
            'reset_code': secret_code, 'expiry_time': expiry_time}

        # send email
        em = EmailMessage()
        EMAIL_ADDRESS = "BadgerCOMP1531@gmail.com"
        EMAIL_PASSWORD = "BADGER1531"

        em['Subject'] = 'Seams Password Reset'
        em['From'] = "Seams Admin"
        em['To'] = email
        htmlEmailPrefix = """<!DOCTYPE html><html><body>"""
        htmlEmailSuffix = """ </body></html>"""
        msg = f"""Dear {found_user[U_NAME_FIRST_IDX]} {found_user[U_NAME_LAST_IDX]}, We received a
        request from you to reset your password to the Seams platform. You may reset your password
        by clicking the following link: {URL + "passwordreset"} and entering the following security code: {secret_code}"""
        em.add_alternative(htmlEmailPrefix+msg+htmlEmailSuffix, subtype='html')
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(em)

        data_store.set(store)


def password_reset_reset_v1(new_password, secret_code):
    '''
    Description: 'password_reset_reset_v1' is the second half of the password reset functionality and
        is designed to authorise a new password change and update the new password given. The 
        function takes in a new password, which must meet the register criteria and is also given a
        secret code to validate the user.

    Arguments:
        'new_password' - A string representing the new password for a user
        'secret_code' - A random 6 digit security code

    Exceptions: 
        InputError occurs when new_password is less than 6 characters
        InputError occurs when the reset code is incorrect 

    Return Value:
        {} - Returns empty dictionary
    '''
    store = data_store.get()

    if len(new_password) < 6:
        raise InputError("Password length must be more than 6 characters")

    for idx, user in enumerate(store['users']):
        if user[U_PW_RESET_CODE_IDX]['reset_code'] == secret_code and \
                user[U_PW_RESET_CODE_IDX]['expiry_time'] > time.mktime(datetime.now().timetuple()):
            user_found = True
            hash_object = hashlib.sha1(new_password.encode())
            password_encrypted = hash_object.hexdigest()
            store['users'][idx][U_PASSWORD_IDX] = password_encrypted

    if not user_found:
        raise InputError("Invalid reset code")

    u_id = user[U_ID_IDX]

    logout_list = []
    for session in store['sessions']:
        data = jwt.decode(session, key="BADGER", algorithms=['HS256'])
        if u_id == data['auth_user_id']:
            logout_list.append(session)

    data_store.set(store)
    for session in logout_list:
        auth_logout_v1(session)

    return {}, 200

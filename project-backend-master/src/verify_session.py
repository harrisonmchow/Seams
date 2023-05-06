'''
verify_session.py:

A helper file designed to validate whether a user is currently logged in.

Functions:
    verify_session(user_token)
'''
import jwt
from src.data_store import data_store, U_ID_IDX
from src.error import AccessError


def verify_session(user_token):
    '''
    Verify session searches for a user's token in a list of current sessions.

    Arguments: 
        user_token: The json web token associated with the user being verified. 

    Return Value:
        auth_user_id: A dictionary containing the individuals auth_user_id.
    '''
    #
    # Session is valid if it exists in the session store
    #
    store = data_store.get()
    found_session = False
    for session in store['sessions']:
        if user_token == session:
            found_session = True
            break

    if found_session:
        data = jwt.decode(user_token, key="BADGER", algorithms=['HS256'])
        auth_user_id = data['auth_user_id']
    else:
        raise AccessError(
            description="User not authorised (not logged in)") from AccessError

    return auth_user_id

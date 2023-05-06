'''
search.py:

This script allows the user to search all messages in history based on a query.
Data_Store is accessed and search is applied on all messages

Functions:
    search_v1(token, query_str)
'''
from src.data_store import data_store
from src.error import InputError
from src.verify_session import verify_session


def search_v1(token, query_str):
    '''
    This function takes in a token of an existing Seams user
    A query string which is used to search for messages to be contained
    All messages containing this keyword/string will be returned.

    Arguments:
        token (str) - A JWT which identifies a user
        query_str (str) - A string containing keywords to be searched

    Exceptions:
        InputError  - Occurs when a query_str is less than 1 or bigger than 1000 in length
        AccessError - Occurs when session is invalid (verify_session fails)

    Return Value:
        Returns {messages}
    '''
    verify_session(token)
    ret_msgs = []
    data = data_store.get()

    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(
            'query cannot be empty or longer than 1000 characters')

    for message_ch in data['messages']:
        for message in message_ch:
            if query_str.casefold() in message['message'].casefold():
                ret_msgs.append(message)

    for message_dm in data['dm_messages']:
        for message in message_dm:
            if query_str.casefold() in message['message'].casefold():
                ret_msgs.append(message)

    return {'messages': ret_msgs}

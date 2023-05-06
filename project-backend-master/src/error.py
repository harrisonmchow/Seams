

from werkzeug.exceptions import HTTPException


class AccessError(HTTPException):
    code = 403
    message = 'ACCESS ERROR'


class InputError(HTTPException):
    code = 400
    message = 'No message specified'


"""
class AccessError(Exception):
    '''Defines AccessError as an Exception'''
    pass


class InputError(Exception):
    '''Defines InputError as an Exception'''
    pass
"""

''' import for testing dm_list function '''
import pytest
from flask import Flask, request
from flask_cors import CORS

from src.server import clear_v2
from src.dm import dm_create_v1
from src.dm import dm_list_v1
# from src.user import user_register
from src.auth import auth_register_v2, auth_login_v2

APP = Flask(__name__)
CORS(APP)

@pytest.fixture
def clear_register_user_and_reset():
    '''
    This function creates auth and member users
    which are used to test the dm/list function
    '''
    clear_v2()                                                  # Clear data
    user_all = []
    dm_all = []
    auth_register_v2('felix.li@vtub.er',
                     'emptied', 'felix', 'li')
    user_all.append(auth_login_v2('felix.li@vtub.er',
                     'emptied'))               # Create user (auth)
    
    auth_register_v2('mako.fuka@vtub.er',
                     'passwor', 'mako', 'fuka')
    user_all.append(auth_login_v2('mako.fuka@vtub.er',
                     'passwor'))              # Create user (member)
    
    auth_register_v2('homou.nene@vtub.er',
                     'ceet2u3', 'homou', 'nene')
    user_all.append(auth_login_v2('homou.nene@vtub.er',
                     'ceet2u3'))             # Create user (member)
    
    
    dm_all.append(dm_create_v1(user_all[0]['token'], [ user_all[1]['auth_user_id'],
                                                       user_all[2]['auth_user_id'] ]))
    dm_all.append(dm_create_v1(user_all[1]['token'], [ user_all[2]['auth_user_id'] ]))

    return user_all, dm_all


def test_dm_list_type(clear_register_user_and_reset):
    '''
    This function tests output types of dm_list
    Here we are assuming dm_list is a list of dm_ids
    The above return types are not specified in markup
    '''

    users, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    output = dm_list_v1(users[2]['token'])
    assert isinstance(output['dms'], list)
    assert isinstance(output['dms'][0], dict)


def test_dm_list_empty(clear_register_user_and_reset):
    '''
    This function tests if the user doesn't belong to any dms
    '''
    users, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    auth_register_v2('lu.lu@niji.retired',
                  'conlulu', 'lu', 'lu')
    users.append(auth_login_v2('lu.lu@niji.retired',
                  'conlulu'))

    output = dm_list_v1(users[3]['token'])
    assert not output['dms']


def test_dm_list_creator(clear_register_user_and_reset):
    '''
    This function tests if owner gets dm_list
    owner's u_id is not included in u_ids
    but it should also return it dm_list normally
    '''
    users, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    output = dm_list_v1(users[1]['token'])
    print(output)
    assert output['dms'][0]['dm_id'] == dm_all[0]['dm_id']
    assert output['dms'][1]['dm_id'] == dm_all[1]['dm_id']

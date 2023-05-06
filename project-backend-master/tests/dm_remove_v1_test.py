''' import for testing dm_list function '''
import pytest

from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.server import clear_v2
from src.dm import dm_create_v1
from src.dm import dm_remove_v1
from src.dm import dm_list_v1
from src.dm import dm_leave_v1
# from src.user import user_register
from src.auth import auth_register_v2, auth_login_v2


@pytest.fixture
def clear_register_user_and_reset():
    '''
    This function creates auth and member users
    which are used to test the dm/remove function
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


def test_remove_invalid_id(clear_register_user_and_reset):
    '''
    Test if an invalid dm_id is provided
    '''
    user_all, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    with pytest.raises(InputError):
        dm_remove_v1(user_all[0]['token'], 9999)


def test_remove_not_authorised(clear_register_user_and_reset):
    '''
    Test if an unauthorised user is calling
    '''
    user_all, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    with pytest.raises(AccessError):
        dm_remove_v1(user_all[2]['token'], dm_all[0]['dm_id'])
    
    with pytest.raises(AccessError):
        dm_remove_v1(user_all[1]['token'], dm_all[0]['dm_id'])


def test_remove_owner_left(clear_register_user_and_reset):
    '''
    Test if former owner can initiate remove option
    The owner must have left the group
    '''

    user_all, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    dm_leave_v1(user_all[0]['token'], dm_all[0]['dm_id'])

    with pytest.raises(AccessError):
        dm_remove_v1(user_all[0]['token'], dm_all[0]['dm_id'])


def test_remove_working(clear_register_user_and_reset):
    '''
    Test if dm_remove works in normal circumstance
    Removes all users from the DM (including owner)
    Will NOT delete the entry form data_store
    i.e. dm_id is untouched, msg is untouched
    '''

    user_all, dm_all = clear_register_user_and_reset
    store = data_store.get()

    # check dm_all validity
    print(dm_all)

    dm_remove_v1(user_all[0]['token'], dm_all[0]['dm_id'])

    assert len(store['dms']) == 2
    print(store['dms'])

    list_output = dm_list_v1(user_all[2]['token'])
    assert len(list_output['dms']) == 1

''' import for testing dm_leave function '''
import pytest

from src.data_store import data_store, DM_OWN_IDX, DM_MEMBERS_IDX
from src.error import InputError
from src.error import AccessError
from src.server import clear_v2
from src.dm import dm_create_v1
from src.dm import dm_details_v1
from src.dm import dm_leave_v1
# from src.user import user_register
from src.auth import auth_register_v2, auth_login_v2


@pytest.fixture
def clear_register_user_and_reset():
    '''
    This function creates auth and member users
    which are used to test the dm/leave function
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


def test_leave_invalid_id(clear_register_user_and_reset):
    '''
    Test if an invalid dm_id is provided
    '''
    user_all, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    with pytest.raises(InputError):
        dm_leave_v1(user_all[0]['token'], 9999)


def test_details_unauthorised(clear_register_user_and_reset):
    '''
    Test if an user that is not a member calls the function
    '''
    user_all, dm_all = clear_register_user_and_reset
    
    # check dm_all validity
    print(dm_all)

    auth_register_v2('lu.lu@niji.retired',
                  'conlulu', 'lu', 'lu')
    user_all.append(auth_login_v2('lu.lu@niji.retired',
                  'conlulu'))

    with pytest.raises(AccessError):
        dm_leave_v1(user_all[3]['token'], dm_all[0]['dm_id'])


def test_member_leave(clear_register_user_and_reset):
    '''
    Tests if channel name is altered if member leaves
    Tests if channel member list changes if member leaves (including owner)
    '''

    user_all, dm_all = clear_register_user_and_reset
    store = data_store.get()
    # check dm_all validity
    print(dm_all)

    # data_store abnormal behavior
    print(store['dms'][0])

    output_ini = dm_details_v1(user_all[0]['token'], dm_all[0]['dm_id'])
    dm_leave_v1(user_all[2]['token'], dm_all[0]['dm_id'])
    output_aft = dm_details_v1(user_all[0]['token'], dm_all[0]['dm_id'])

    assert output_ini['name'] == output_aft['name']
    assert len(output_ini['members']) == len(output_aft['members']) + 1


# implement test_owner_leave: owner status will update, but will not disappear
def test_owner_leave(clear_register_user_and_reset):
    '''
    Tests if channel name is altered if member leaves
    Tests if channel member list changes if member leaves (including owner)
    '''

    user_all, dm_all = clear_register_user_and_reset
    store = data_store.get()

    # check dm_all validity
    print(dm_all)

    output_ini = dm_details_v1(user_all[0]['token'], dm_all[0]['dm_id'])
    print(store['dms'][0])
    dm_leave_v1(user_all[0]['token'], dm_all[0]['dm_id'])
    print(store['dms'][0])
    with pytest.raises(AccessError):
        dm_details_v1(user_all[0]['token'], dm_all[0]['dm_id'])
    

    assert store['dms'][0][DM_OWN_IDX]['status'] == 'left'
    print(store['dms'][0][DM_MEMBERS_IDX])
    print(output_ini['members'])
    assert store['dms'][0][DM_OWN_IDX] not in output_ini['members']
    assert store['dms'][0][DM_MEMBERS_IDX][0][0] == output_ini['members'][0]['u_id']


# reserve a spot for @APP, currently unused

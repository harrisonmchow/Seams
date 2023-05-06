''' import for testing dm_create function '''
import pytest

from src.data_store import data_store
from src.error import InputError    
from src.server import clear_v2
from src.dm import dm_create_v1
# from src.user import user_register
from src.auth import auth_register_v2, auth_login_v2


@pytest.fixture
def clear_register_user_and_reset():
    '''
    This function creates auth and member users
    which are used to test the dm/create function
    '''
    clear_v2()                                                # Clear data
    user_all = []
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

    return user_all


def test_dm_create_invalid(clear_register_user_and_reset):
    '''
    Tests invalid user_id in u_ids list
    '''
    user_list = clear_register_user_and_reset
    
    with pytest.raises(InputError):
        dm_create_v1(user_list[0]['token'], [10])


def test_dm_create_empty(clear_register_user_and_reset):
    '''
    Tests owner creating a testing DM, in other word a DM with no other members
    The DM should be created within data_store['dms'] with dm_id 0x1
    '''
    user_list = clear_register_user_and_reset
    store = data_store.get()
    new_dm_id = dm_create_v1(user_list[0]['token'], [])
    assert new_dm_id['dm_id'] == 1
    print(store['dms'])
    assert new_dm_id['dm_id'] == store['dms'][0][0]


def test_dm_create_dupe(clear_register_user_and_reset):
    '''
    Tests duplicate user_id in u_ids list
    '''
    user_list = clear_register_user_and_reset

    with pytest.raises(InputError):
        dm_create_v1(user_list[0]['token'], [ user_list[1]['auth_user_id'],
                                              user_list[1]['auth_user_id'],
                                              user_list[2]['auth_user_id'] ])


def test_dm_create_type(clear_register_user_and_reset):
    '''
    Make sure dm_create returns the correct type
    '''
    user_list = clear_register_user_and_reset
    dm_1 = dm_create_v1(user_list[0]['token'], [ user_list[1]['auth_user_id'],
                                                 user_list[2]['auth_user_id'] ])
    dm_2 = dm_create_v1(user_list[1]['token'], [ user_list[2]['auth_user_id'] ])

    assert isinstance(dm_1['dm_id'], int)
    assert isinstance(dm_2['dm_id'], int)

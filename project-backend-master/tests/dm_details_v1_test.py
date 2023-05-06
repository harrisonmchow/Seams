''' import for testing dm_list function '''
import pytest

from src.error import InputError
from src.error import AccessError
from src.server import clear_v2
from src.dm import dm_create_v1
from src.dm import dm_details_v1
# from src.user import user_register
from src.auth import auth_register_v2, auth_login_v2


@pytest.fixture
def clear_register_user_and_reset():
    '''
    This function creates auth and member users
    which are used to test the dm/details function
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


def test_details_invalid_id(clear_register_user_and_reset):
    '''
    Test if an invalid dm_id is provided
    '''
    user_all, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    with pytest.raises(InputError):
        dm_details_v1(user_all[0]['token'], 9999)


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
        dm_details_v1(user_all[3]['token'], dm_all[0]['dm_id'])


def test_details_type(clear_register_user_and_reset):
    '''
    Test if details return the correct type
    '''

    user_all, dm_all = clear_register_user_and_reset

    # check dm_all validity
    print(dm_all)

    test_return = dm_details_v1(user_all[0]['token'], dm_all[0]['dm_id'])

    assert isinstance(test_return['name'], str)
    assert isinstance(test_return['members'], list)
    assert isinstance(test_return['members'][0]['u_id'], int)
    assert isinstance(test_return['members'][0]['email'], str)
    assert isinstance(test_return['members'][0]['name_first'], str)
    assert isinstance(test_return['members'][0]['name_last'], str)
    assert isinstance(test_return['members'][0]['handle_str'], str)


# reserve a spot for @APP, currently unused

''' import for testing dm_list function '''
import pytest

from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.server import clear_v2
from src.dm import dm_create_v1
from src.dm import dm_details_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1, channel_invite_v1, channel_addowner_v1
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
    channel_all = []
    store = data_store.get()
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

    channel_all.append(channels_create_v1(user_all[0]['auth_user_id'], 'rizu_ch', True))
    print(f'Channel info: {channel_all}')
    print(f'All Channels: ', end='')
    print(store['channels'])
    channel_join_v1(user_all[1]['auth_user_id'], channel_all[0]['channel_id'])
    channel_join_v1(user_all[2]['auth_user_id'], channel_all[0]['channel_id'])
    
    channel_all.append(channels_create_v1(user_all[1]['auth_user_id'], 'mafu_ch', False))
    print(f'Channel info: {channel_all}')
    print(f'All Channels: ', end='')
    print(store['channels'])
    channel_invite_v1(user_all[1]['auth_user_id'],
                      channel_all[1]['channel_id'],
                      user_all[2]['auth_user_id'])

    return user_all, channel_all


def test_user_not_authorised_local(clear_register_user_and_reset):
    '''
    Test if an unauthorised user is calling this function, it should raise access error
    By non-autorised it means either not an owner of the channel
    Or not a global owner who is a member of the current channel
    HTTP test
    '''
    user_all, channel_all = clear_register_user_and_reset
    store = data_store.get()
    print(user_all)
    # check channels_all availability
    print(channel_all)
    print(store['channels'])

    with pytest.raises(AccessError):
        channel_addowner_v1(user_all[2]['token'], channel_all[0]['channel_id'], user_all[1]['auth_user_id'])
    
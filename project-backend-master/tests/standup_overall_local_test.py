'''
This script runs under the non-server environment, intended to be used for
the detection of dead branches which coverage doesn not cover despite
the tests running them on multiple instances

Functions:
    standup_start_v1
    standup_active_v1
    standup_send_v1

Local Test
'''
from src.error import InputError, AccessError
from src.auth import auth_register_v2, auth_logout_v1
from src.channels import channels_create_v1
from src.message import check_message_send_later
from src.channel import channel_leave_v1, channel_messages_v1, channel_join_v1, channel_invite_v1
from src.standup import standup_running, standup_start_v1, standup_active_v1, standup_send_v1
from src.other import check_channel_id, clear_v1

import pytest
import time


@pytest.fixture
def clear_register_and_reset_local():
    clear_v1()
    users = []
    latent_users = []
    channels = []

    users.append(auth_register_v2('felix.li@vtub.er',
                                  'emptied', 'felix', 'li'))
    users.append(auth_register_v2('mako.fuka@vtub.er',
                                  'passwor', 'mako', 'fuka'))
    users.append(auth_register_v2('homou.nene@vtub.er',
                                  'ceet2u3', 'homou', 'nene'))
    latent_users.append(auth_register_v2('mike.neko@vtub.er',
                                  'uruha_rushia', 'mike', 'neko'))
    latent_users.append(auth_register_v2('ceres.fauna@holo.en',
                                  'uuunotthis', 'ceres', 'fauna'))
    latent_users.append(auth_register_v2('kson.onair@holo.en',
                                  'asacoco', 'kson', 'onair'))
    latent_users.append(auth_register_v2('nana.tatsudaki@vtub.er',
                                  'data_science', 'nana', 'tatsudaki'))

    channels.append(channels_create_v1(
                users[1]['auth_user_id'], 'mako_ch', True))
    channel_join_v1(users[0]['auth_user_id'], channels[0]['channel_id'])
    channel_join_v1(users[2]['auth_user_id'], channels[0]['channel_id'])
    channel_join_v1(
                latent_users[3]['auth_user_id'], channels[0]['channel_id'])

    channels.append(channels_create_v1(
                users[2]['auth_user_id'], 'nene_ch', False))
    channel_invite_v1(users[2]['auth_user_id'],
                channels[1]['channel_id'], latent_users[3]['auth_user_id'])

    channels.append(channels_create_v1(
                latent_users[1]['auth_user_id'], 'fauna_ch', True))
    channel_join_v1(users[0]['auth_user_id'], channels[2]['channel_id'])
    channel_join_v1(
                latent_users[0]['auth_user_id'], channels[2]['channel_id'])

    return {
    	'users': users,
        'latent_users': latent_users,
    	'channels': channels,
    }


def test_standup_fiddle(clear_register_and_reset_local):
    '''
    This test simulates 2 newly registrated users,
    a newly registered public channel, and two pre-existing channels, private and public
    Standups are started, including sending message after standup has finished, and not sending at all during period

    This is a local test
    '''

    data = clear_register_and_reset_local

    users = data['users']
    latent_users = data['latent_users']
    channels = data['channels']

    t_end_0 = standup_start_v1(users[0]['token'], channels[0]['channel_id'], 2)
    with pytest.raises(AccessError):
        # not a member
        standup_start_v1(users[0]['token'], channels[1]['channel_id'], 1)
    t_end_2 = standup_start_v1(users[0]['token'], channels[2]['channel_id'], 2)

    with pytest.raises(InputError):
        # standup already running
        standup_start_v1(users[2]['token'], channels[0]['channel_id'], 1)
    
    channel_leave_v1(users[0]['auth_user_id'], channels[0]['channel_id'])
    with pytest.raises(AccessError):
        standup_send_v1(users[0]['token'],
                        channels[0]['channel_id'], 'Yoo where\'s the stream?')

    t_end_1 = standup_start_v1(
                    latent_users[3]['token'], channels[1]['channel_id'], 2)
    
    standup_send_v1(users[2]['token'],
                    channels[0]['channel_id'], 'Yoo where\'s the stream?')
    standup_send_v1(latent_users[3]['token'],
                    channels[0]['channel_id'], 'Mako\'s Twitch')

    standup_send_v1(users[0]['token'],
                    channels[2]['channel_id'], 'User stream is being tested')

    with pytest.raises(AccessError):
        standup_send_v1(latent_users[3]['token'],
                        channels[2]['channel_id'], 'Can you ensure channel integrity?')
    channel_join_v1(latent_users[3]['auth_user_id'], channels[2]['channel_id'])

    standup_send_v1(latent_users[3]['token'],
                    channels[2]['channel_id'], 'Can you ensure channel integrity?')

    standup_send_v1(users[1]['token'],
                    channels[0]['channel_id'], 'As long as saplings can connect, all is good')

    standup_send_v1(latent_users[3]['token'],
                    channels[2]['channel_id'], 'I think the server is not very stable')
    
    time.sleep(2)
    with pytest.raises(InputError):
        standup_send_v1(latent_users[2]['token'],
                        channels[0]['channel_id'], 'It should be fine now')
    
    assert time.time() > t_end_0['time_finish']
    assert time.time() > t_end_1['time_finish']
    assert time.time() > t_end_2['time_finish']

    check_message_send_later(users[0]['token'])
    msg_0 = channel_messages_v1(users[1]['auth_user_id'], channels[0]['channel_id'], 0)
    msg_1 = channel_messages_v1(users[2]['auth_user_id'], channels[1]['channel_id'], 0)
    msg_2 = channel_messages_v1(users[0]['auth_user_id'], channels[2]['channel_id'], 0)

    assert len(msg_1['messages']) == 0
    assert msg_0['messages'][0]['message'] == 'homounene: Yoo where\'s the stream?\nnanatatsudaki: Mako\'s Twitch\nmakofuka: As long as saplings can connect, all is good\n'
    assert msg_2['messages'][0]['message'] == 'felixli: User stream is being tested\nnanatatsudaki: Can you ensure channel integrity?\nnanatatsudaki: I think the server is not very stable\n'


def test_standup_bombard(clear_register_and_reset_local):
    '''
    This test is to simulate intentional tampering to Seams channels
    Various users, new and old are to spam standup functions, invite and leave
    standup/send's pre-existing vulnerability is also to be tested here

    This is an HTTP test
    Intended to be run on Linux / BSD
    '''
    pass

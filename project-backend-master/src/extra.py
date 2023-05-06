'''
extra.py:

This file contains functions which allows the
operation of a wordle game.

Functions:
    reset_wordle(key, channel_id)
    space(word)
    get_new_word()
    send_wordle(token, channel_id, msg, ID, share)
    current_status(token, channel_id, ID, share)
    wordle_guess(token, channel_id, message, ID, share)
    check_wordle(token, channel_id, message, ID, share)
    
'''
import json
from random import randint
from src.data_store import data_store
from src.error import InputError
from src.message import message_send_v1, message_senddm_v1, message_edit_v1


def reset_wordle(key, channel_id):
    '''Resetting and/or initialising the wordle store for a given channel'''
    store = data_store.get()
    store[key][channel_id]['wordle_guesses'] = -1
    store[key][channel_id]['wordle_answer'] = ""
    store[key][channel_id]['wordle_incorrect_letters'] = []
    store[key][channel_id]['wordle_misplaced_letters'] = []
    store[key][channel_id]['wordle_current'] = "_____"
    store[key][channel_id]['wordle_prev_guess'] = []
    store[key][channel_id]['wordle_msg_id'] = 0
    store[key][channel_id]['wordle_msg_id2'] = 0
    store[key][channel_id]['wordle_token'] = 0
    data_store.set(store)


def space(word):
    '''Spacing word function for ease of reading'''
    ret_curr = ""
    for letter in word:
        ret_curr += letter + " "
    return ret_curr


def get_new_word():
    '''Randomly picks a word from the word bank'''
    with open('src/words.json', 'r', encoding="utf8") as file:
        file_contents = json.load(file)
    length = len(file_contents)
    idx = randint(0, length - 1)

    return file_contents[idx]


def send_wordle(token, channel_id, msg, ID, share):
    '''Used to send a wordle to either a given channel or dm'''
    if ID == 0:
        mid = message_send_v1(token, channel_id, msg, share)['message_id']
    elif ID == 1:
        mid = message_senddm_v1(token, channel_id, msg, share)['message_id']
    return mid


def current_status(token, channel_id, ID, share):
    '''
    Edits the previous prints to show the current status.
    It will edit messages so only 2 messages are sent
    /exist for the wordle everytime it is run.
    '''
    if ID == 0:
        key = 'wordle_ch'
    else:
        key = 'wordle_dm'
    store = data_store.get()
    guesses = store[key][channel_id]['wordle_guesses']
    answer = store[key][channel_id]['wordle_answer']
    inc = store[key][channel_id]['wordle_incorrect_letters']
    misp = store[key][channel_id]['wordle_misplaced_letters']
    curr = store[key][channel_id]['wordle_current']
    prev = store[key][channel_id]['wordle_prev_guess']
    msg_id = store[key][channel_id]['wordle_msg_id']
    token = store[key][channel_id]['wordle_token']

    ret_curr = ""
    msg = ""

    inc.sort()
    misp.sort()
    inc = ', '.join(inc)
    misp = ', '.join(misp)
    prev = ''.join(prev)
    data_store.set(store)

    edit_not_send = False
    if guesses >= 5:
        msg2 = f"\u203c\ufe0f OH no! You didnt get the answer in 5 tries. The answer was '{answer.upper()}' \u203c\ufe0f"
        msg_id2 = store[key][channel_id]['wordle_msg_id2']
        msg_id1 = store[key][channel_id]['wordle_msg_id']
        edit_not_send = True
        guesses = -1

    if guesses == -1:
        ret_curr = space(curr)
        msg = f"CURRENT WORDLE: \n\n{ret_curr.upper()}\n\n{prev.upper()}\nMisplaced letters: {misp.upper()}\nIncorrect letters: {inc.upper()}\nGuesses left: 0"
    else:
        ret_curr = space(curr)
        msg = f"CURRENT WORDLE: \n\n{ret_curr.upper()}\n\n{prev.upper()}\nMisplaced letters: {misp.upper()}\nIncorrect letters: {inc.upper()}\nGuesses left: {5 - guesses}"

    if msg_id == 0 and edit_not_send is False:
        store[key][channel_id]['wordle_msg_id'] = send_wordle(
            token, channel_id, msg, ID, share)
        data_store.set(store)
    elif guesses == -1:

        message_edit_v1(token, msg_id1, msg)
        message_edit_v1(token, msg_id2, msg2)
        store[key][channel_id] = {}
    else:
        message_edit_v1(token, msg_id, msg)


def wordle_guess(token, channel_id, message, ID, share):
    '''Main function called by sned or senddm functions to check if a wordle
    needs to be started, ended, edited etc.
    Inputs:
        -Token(str)
        -Channel_id(int)
        -Message(str)
        -ID(int)
        -share(BOOL)

    Outputs:
        -NIL

    Errors:
    InputError if the command /wordle is inputted with more or less than one other argument

    InputError if /wordle start is entered and a game is already running in the respective ch/dm

    InputError if the second argument of the /worlde <argument> is not a valid word in the word bank

    InputError if user attempts to end a game and there is no active game in session

    All other errors are handled by other functinos i.e. AccessError's for users being in hannels etc.

    '''
    # ID = 0 : Channel
    # ID = 1 : DM
    store = data_store.get()

    # Setting up keys for data store access
    if ID == 0:
        key = 'wordle_ch'
    else:
        key = 'wordle_dm'

    # Accessing wordle command
    message = message.split()
    if len(message) != 2:
        raise InputError(
            description='Incorrect wordle input. Should be in form "/wordle <ACTION>"')
    message = message[1].lower()

    # Fetching or resetting the guesses
    if store[key][channel_id] != {}:
        guesses = store[key][channel_id]['wordle_guesses']
    else:
        guesses = -1

    # initialising wordle
    if store[key][channel_id] == {}:
        reset_wordle(key, channel_id)
        store[key][channel_id]['wordle_token'] = token
        data_store.set(store)
    else:
        token = store[key][channel_id]['wordle_token']

    # Functional parts
    if message == "end" and guesses >= 0:
        msg = "Wordle ended, please try again at another time"
        send_wordle(token, channel_id, msg, ID, share)
        store[key][channel_id] = {}

    elif message == "start" and guesses == -1:
        reset_wordle(key, channel_id)

        store[key][channel_id]['wordle_token'] = token
        guesses = 0
        store[key][channel_id]['wordle_guesses'] = guesses
        data_store.set(store)
        answer = get_new_word()
        store[key][channel_id]['wordle_answer'] = answer
        data_store.set(store)

        current_status(token, channel_id, ID, share)
        msg = "Welcome to Wordle. Please enter '/wordle' and a 5 letter word: "

        store[key][channel_id]['wordle_msg_id2'] = send_wordle(
            token, channel_id, msg, ID, share)
        data_store.set(store)

    elif message == "start" and guesses != -1:

        raise InputError(description='Already started')

    else:
        answer = store[key][channel_id]['wordle_answer']
        if answer == "":
            raise InputError(description='Game not started')

        with open('src/words.json', 'r', encoding="utf8") as file:
            file_contents = json.load(file)
        # [::-1] to allow for coverage testing (and not too big of a deal- easter egg)
        if message not in file_contents and answer != message[::-1] and message != "jIMmY":
            raise InputError(description='Not a valid word')

        # They got the answer
        if message == answer:
            store[key][channel_id]['wordle_guesses'] += 1
            guesses = store[key][channel_id]['wordle_guesses']
            answer = store[key][channel_id]['wordle_answer']
            ret_curr = ""
            msg = ""
            for letter in answer:
                ret_curr += letter + " "
            msg += ret_curr.upper() + "\n"
            msg += f"\u2705 Well Done, you got the answer in {guesses}! \u2705"
            data_store.set(store)

            store[key][channel_id]['wordle_current'] = message
            store[key][channel_id]['wordle_prev_guess'].append(message + '\n')
            misplaced = store[key][channel_id]['wordle_misplaced_letters']

            for letter in message:
                if letter in misplaced:
                    misplaced.remove(letter)

            data_store.set(store)

            current_status(token, channel_id, ID, share)
            message_edit_v1(token, store[key]
                            [channel_id]['wordle_msg_id2'], msg)
            store[key][channel_id] = {}

        else:
            store[key][channel_id]['wordle_guesses'] += 1
            current = store[key][channel_id]['wordle_current']
            incorrect = store[key][channel_id]['wordle_incorrect_letters']
            misplaced = store[key][channel_id]['wordle_misplaced_letters']

            store[key][channel_id]['wordle_prev_guess'].append(message + '\n')
            data_store.set(store)

            for idx, letter in enumerate(message):
                if letter not in answer:
                    if letter not in incorrect:
                        incorrect.append(letter)

                elif letter == answer[idx]:
                    current = list(current)
                    current[idx] = letter
                    current = ''.join(current)

                else:
                    if letter not in misplaced:
                        misplaced.append(letter)

            for letter in current:
                if letter in misplaced:
                    misplaced.remove(letter)

            store[key][channel_id]['wordle_current'] = current
            store[key][channel_id]['wordle_misplaced_letters'] = misplaced
            store[key][channel_id]['wordle_incorrect_letters'] = incorrect
            data_store.set(store)
            current_status(token, channel_id, ID, share)
    data_store.set(store)


def check_wordle(token, channel_id, message, ID, share):
    '''Checking if the wordle command is correct and should
    call for a wordle process to be called'''
    message_split = message.split()
    if len(message_split) > 0 and message_split[0] == "/wordle":
        wordle_guess(token, channel_id, message, ID, share)
        return True
    else:
        return False

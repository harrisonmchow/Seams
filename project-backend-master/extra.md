EXTRA FEATURES!!!

Description:
    The an adaptation for the game of WORDLE has been added to Seams. A game of WORDLE can be started in a channel or dm, and is played through the chat/message function. only one game can be running per channel, and users must enter their guess for the word and the WORDLE game is updated and displayed in the same chat until the answer is found, or the 5 tries have been used.

Function:
    to use the wordle game all commands are two arguments, and must be type in the textbox/message as '/wordle <action>'.
    
    actions:
    /wordle start: starts a game of wordle in the given channel or dm chat. Can only start if there is not an active game already in the ch/dm
    /wordle end: Ends a game no matter what, a new game can be started after this with a new randomly picked word
    /wordle <guess> : can be played once a game is in progress, will take in the guess and compare and output correct letters, misplaces letters, and incorrect letters, as well as the previous guess and tries left.

Errors:
    InputError if the command /wordle is inputted with more or less than one other argument

    InputError if /wordle start is entered and a game is already running in the respective ch/dm

    InputError if the second argument of the /worlde <argument> is not a valid word in the word bank

    InputError if user attempts to end a game and there is no active game in session

    All other errors are handled by other functinos i.e. AccessError's for users being in hannels etc.

General Assumptions:
 - Assuming that an owner is always a member of the channel, as well as being an owner.

For channel_join_v1:
 - Assuming that the channel_id will only be given as an integer of base 10

For channel_details:
 - It is assumed that at least one user exists and is registered and stored in the user store for the details to work.
 - As per the spec it is assumed that the auth_user_id is valid and does not need to be checked

For auth_register_v1:
 - It is assumed that "name_first" and "name_last" must only contain alphabetic characters
 - User ID's start from 1
 - Password must be between 6 and 30 characters so that users cannot store an infinitely long password

For auth_login_v1:
 - Login is accepted even when user is already logged in

For channels_create_v1:
 - The creator of the channel is added to the owner list
 - Channel ID's start from 1
 - The auth_user_id parameter is a valid user id.

 For channel_messages_v1:
 - Assuming 'start' and 'end' are integers
 - Within 'channels' from datastore
 
 For channel/messages/v2:
 - If there are no messages, I assume that the http route should run and simply display no messages

 For message/react/v1:
 - It is assumed that a user is a member of the chanel/dm which the message they are trying to react exists in.

 For users/stats/v1:
 - When a dm is removed containing messages, they are all removed at once. So for example, if there a 6 total messages, 3 of which are in a dm which is then removed, the number of messages that exist (when looking at it from users/stats/v1) goes from 6 to 3 (instead of 6 to 5 to 4 to 3). 

 For message/sendlater/v1 and message/sendlaterdm/v1:
 - The time that the message is to be sent can be the current time (so it acts exactly like message/send/v1)

 For users/stats/v1:
- Deleted users aren't counted in the utilization rate
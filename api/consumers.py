# ref: https://realpython.com/getting-started-with-django-channels/
import json
from channels import Group # deprecated
#from channels.layers import get_channel_layer
from channels.auth import channel_session_user, channel_session_user_from_http
#from asgiref.sync import async_to_sync
#channel_layer = get_channel_layer()

@channel_session_user_from_http
def ws_connect(message):
    #if user.is_authenticated:
    #    Group("user-{}".format(user.id)).add(message.reply_channel)
    Group('users').add(message.reply_channel)
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': True
        })
    })

@channel_session_user
def ws_disconnect(message):
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': False
        })
    })
    Group('users').discard(message.reply_channel)


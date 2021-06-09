# ref: https://realpython.com/getting-started-with-django-channels/
import json
from channels import Group # deprecated
#from channels.layers import get_channel_layer
from channels.auth import channel_session_user, channel_session_user_from_http
#from asgiref.sync import async_to_sync
#channel_layer = get_channel_layer()
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__file__)

#def initiateHandshake():
#    Group("users").send({"text": "handshake"})

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
def ws_receive(message, http_user=True):
    try:
        #logger.info("Channel session fields: %s" % message.channel_session.__dict__)
        user = User.objects.get(pk=message.channel_session['_auth_user_id'])
        #prefix = message.channel_session['users']
        data = json.loads(message['text'])
        logger.info('Message user=%s auth_user=%s message=%s', message.user, user, data)
        #msg =  users.messages.create(handle=data['handle'], message=data['message'])  #that if need to save msg to database
        Group('users').send({
        #message.reply_channel.send({
            'text': json.dumps({
                'message': data
            })
        })

    except Exception:
        logger.info("ERROR occur in ws_message: %s", message['text']) #%s" % traceback.format_exc())

@channel_session_user
def ws_disconnect(message):
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': False
        })
    })
    Group('users').discard(message.reply_channel)


# channels 1.1.8 ref: https://realpython.com/getting-started-with-django-channels/
#from channels import Group # channels 1.1.8
#from channels.auth import channel_session_user, channel_session_user_from_http
#from django.contrib.auth.models import User
#import json
from datetime import datetime

# channels 3.0
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .exceptions import ClientError
from django.contrib.auth.models import User #, Group
from .models import Message #apiuser, MsgForm
#from django.utils import timezone

import logging
logger = logging.getLogger(__file__)

def is_valid_datetime(dtime):
    try:
        dtime = datetime.fromisoformat(dtime)
        #logger.info("Get a date: %s", dtime)
        return True

    except ValueError:
        return False

def create_message(username, data):
    dueon = data["due"] if is_valid_datetime(data["due"]) else None
    sender = User.objects.get(username=username) #(if use apiuser) user__username: fix the exception Field 'id' expected a number but got...
    logger.info("Now get msg handler: %s, msg: %s, due_on: %s", sender, data['message'], dueon)
    msgobj = Message(handle=sender, message=data['message'], due=dueon)
    msgobj.save()
    #msg = json.loads(json.dumps({ #MsgForm({ #Message.objects.create(
        #    #id=None,
        #    'handle':sender,
        #    'message':data["message"],
        #    'group':'all',
        #    'level':'Normal',
        #    'due': None,
        #    'timestamp': timezone.now
        #}))
    #msgobj = sender.message.create(**msg)
    #logger.info('Message created: %s', msgobj)


# channels 3.0 ref: https://github.com/andrewgodwin/channels-examples
class MsgConsumer(AsyncJsonWebsocketConsumer): #WebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close() # Reject the connection
        #else:
        await self.channel_layer.group_add("users", self.channel_name)
        await self.accept() # Accept the connection

        await self.channel_layer.group_send(
            "users",
            {
                "type": "msg.online", #--> handler: msg_online
                'username': self.scope["user"].username, #essage.user.username
                'is_logged_in': True
            }
        )

    async def receive_json(self, data):
        logger.info('Receive_json user=%s, message=%s, dtime=%s', self.scope["user"].username, data['message'], data['due'])
        try:
            await self.channel_layer.group_send(
                "users",
                {
                    "type": "msg.send", #--> handler: msg_send
                    "message": data["message"],
                    "due": data["due"]
                }
            )
            await sync_to_async(create_message)(self.scope["user"].username, data)

        except ClientError as err:
            await self.send_json({"error": err.code}) # Catch any errors and send it back

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_send(
                "users",
                {
                    "type": "msg.online",
                    'username': self.scope["user"].username, #essage.user.username
                    'is_logged_in': False
                }
            )
            await self.channel_layer.group_discard("users", self.channel_name)

        except ClientError:
            pass

    async def msg_online(self, event):
        await self.send_json({
            'username': event['username'],
            'is_logged_in': event['is_logged_in'],
        })

    async def msg_send(self, event):
        await self.send_json({
            "message": event["message"],
        })


# channels 1.1.8
#@channel_session_user_from_http
#def ws_connect(message):
#    #if user.is_authenticated:
#    #    Group("user-{}".format(user.id)).add(message.reply_channel)
#    Group('users').add(message.reply_channel)
#    Group('users').send({
#        'text': json.dumps({
#            'username': message.user.username,
#            'is_logged_in': True
#        })
#    })

#@channel_session_user
#def ws_receive(message, http_user=True):
#    try:
#        #logger.info("Channel session fields: %s" % message.channel_session.__dict__)
#        user = User.objects.get(pk=message.channel_session['_auth_user_id'])
#        #prefix = message.channel_session['users']
#        data = json.loads(message['text'])
#        logger.info('Message user=%s auth_user=%s message=%s', message.user, user, data)
#        #msg =  users.messages.create(handle=data['handle'], message=data['message'])  #that if need to save msg to database
#        Group('users').send({
#            'text': json.dumps({
#                'message': data
#            })
#        })

#    except Exception:
#        logger.info("ERROR occur in ws_message: %s", message['text']) #%s" % traceback.format_exc())

#@channel_session_user
#def ws_disconnect(message):
#    Group('users').send({
#        'text': json.dumps({
#            'username': message.user.username,
#            'is_logged_in': False
#        })
#    })
#    Group('users').discard(message.reply_channel)


# channels 1.1.8 ref: https://realpython.com/getting-started-with-django-channels/
#from channels import Group # channels 1.1.8
#from channels.auth import channel_session_user, channel_session_user_from_http
#from django.contrib.auth.models import User
#import json
from datetime import datetime #, timezone
from django.utils import timezone

# channels 3.0
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .exceptions import ClientError
from django.contrib.auth.models import User #, Group
from .models import Message, apiuser #, MsgForm

import logging
logger = logging.getLogger(__file__)

#from django.conf import settings
import pytz #handle localtime from js isostring

def is_valid_datetime(dtime, tzone): #=settings.TIME_ZONE):
    try:
        #dtime = datetime.fromisoformat(dtime)
        tz = pytz.timezone(tzone) if tzone and not tzone.isspace() else datetime.now().astimezone().tzinfo
        dtime = datetime.fromisoformat(dtime).replace(tzinfo=tz)
        logger.info("Get a date format: %s in timezone %s", dtime, tz)
        return True

    except ValueError:
        logger.info("Get a Wrong date format: %s in timezone %s", dtime, tzone)
        return False

def has_json_key(json, key):
    try:
        return json[key]

    except KeyError:
        return False


def get_auth_user(username):
    return User.objects.get(username=username)

def create_message(username, data):
    dueon = data["due"] if is_valid_datetime(data["due"], data["tzone"]) else None
    sender = get_auth_user(username) #(if use apiuser) user__username: fix the exception Field 'id' expected a number but got...
    #logger.info("Now get msg handler: %s, msg: %s, due_on: %s", sender, data['message'], dueon)
    msgobj = Message(handle=sender, message=data['message'], due=dueon, level=int(data['level']))
    msgobj.save()
    return msgobj.formatted_message # send a formatted message the same as when query msg_not_seen
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

def create_apiuser(user):
    return apiuser.objects.get_or_create(user=user) #user__username=username

def update_channel_name(user, channel_name):
    #apiuser.objects.filter(user__username=username).update(channel_name=channel_name)
    auser = create_apiuser(user)[0]
    auser.channel_name = channel_name
    auser.save()
    return auser

def get_message_not_seen(last_checked):
    return Message.must_seen(last_checked)

def update_lastchk_time(username): #do it before reconnect(here) and logout (signals.py)
    #return apiuser.objects.filter(user__username=username).update(last_checked=timezone.localtime(timezone.now()), channel_name="") #used when disconnect
    return apiuser.objects.filter(user__username=username).update(last_checked=timezone.localtime(timezone.now())) #used in receive socket from client, not a re-connect signal


# channels 3.0 ref: https://github.com/andrewgodwin/channels-examples
class MsgConsumer(AsyncJsonWebsocketConsumer): #WebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close() # Reject the connection
        #else:

        user = self.scope["user"]
        await self.channel_layer.group_add("users", self.channel_name)

        uobj = await sync_to_async(get_auth_user)(user.username)
        logger.info("auth_name is %s", uobj.username)
        auser= await sync_to_async(update_channel_name)(uobj, self.channel_name)
        #logger.info("channel_name is %s", auser.channel_name) #specific channel for single user

        await self.accept() # Accept the connection

        await self.channel_layer.group_send(
            "users",
            {
                "type": "msg.online", #--> handler: msg_online
                'username': user.username, #essage.user.username
                'is_logged_in': True
            }
        )
        await self.send_last_checked(auser) #send to specific use not_seen message

    async def receive_json(self, data):
        #logger.info("First received message: %s", data)
        if has_json_key(data, "lastchecked"):
            await sync_to_async(update_lastchk_time)(self.scope["user"].username)

        else:
            logger.info('Receive_json user=%s, message=%s, level=%s, dtime=%s timezone=%s', self.scope["user"].username, data['message'], data['level'], data['due'], data['tzone'])
            try:
                msgsave = await sync_to_async(create_message)(self.scope["user"].username, data) #msgsave is MsgLevel + data['message'] + due
                #logger.info("Formatting Group send: %s", msgsave) #send a formatted message the same as when query msg_not_seen
                await self.channel_layer.group_send(
                    "users",
                    {
                        "type": "msg.send", #--> handler: msg_send
                        "message": msgsave, #data["message"],
                        #"due": data["due"],
                        #"tzone": data["tzone"],
                    }
                )

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
            #await sync_to_async(update_lastchk_time)(self.scope["user"].username) #<- it works when reconnect to signal last_checked, but may cause unread message if unintended re-connection
            await self.channel_layer.group_discard("users", self.channel_name)

        except ClientError:
            pass

    async def send_last_checked(self, auser):
        #auser= await sync_to_async(get_apiuser)(user.username)[0]
        msgx = await sync_to_async(get_message_not_seen)(auser.last_checked)

        for msg in msgx:
            #logger.info('Must seen in json: %s', msg.get('message'))
            await self.channel_layer.send(auser.channel_name,
                {
                    'type': 'msg.send',
                    'message': msg.get('message')
                }
            )

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


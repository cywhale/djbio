from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q
from api.models import apiuser #, Message

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

#from api.consumers import MsgConsumer #move to another consumer class
#import logging
#logger = logging.getLogger(__file__)


@receiver(user_logged_in)
def on_user_login(sender, **kwargs): #,user,
    auser=apiuser.objects.get_or_create(user=kwargs.get('user')) #<--it's ok, if 'user' not in argument
#    #logger.info('User logined signal: %s', auser[0])
#    msgx= Message.must_seen(auser[0].last_checked)
#    logger.info('Must seen in json: %s', msgx)
# ----------- move to consumer.py -------------
#    for msg in msgx:
#        async_to_sync(channel_layer.send(auser[0].channel_name,
#            {
#                'type': 'msg.send',
#                'text': msg
#            }
#        ))

@receiver(user_logged_out)
def on_user_logout(sender, user, **kwargs):
    auser=apiuser.objects.filter(
        Q(user__username=user.username) #kwargs.get('user')) #<--it's ok, if 'user' not in argument
        ).update(last_checked=timezone.now(), channel_name="") #.delete() #dont remove otherwise no last_checked
    # Note an exception occur if use only 'timezone.now': expected string or bytes-like object ....dateparse.py in parse_datetime
    # logger.info('User logout and update last_check: %s', auser)

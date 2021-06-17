from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from api.models import apiuser, Message

import logging
logger = logging.getLogger(__file__)

@receiver(user_logged_in)
def on_user_login(sender, **kwargs):
    auser=apiuser.objects.get_or_create(user=kwargs.get('user'))
    logger.info('User logined signal: %s', auser[0])
    msgx= Message.must_seen(auser[0].last_checked)
    logger.info('Must seen in json: %s', msgx)


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    apiuser.objects.filter(user=kwargs.get('user')).delete()

#from __future__ import unicode_literals
from django.db import models
#from django.forms import ModelForm
#from django.contrib.gis.db import models
from django.contrib.auth.models import Group, User
#from django.db.models import JSONField
# Django 2.2.23
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField #Django 3.2.3
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
import json

import logging
logger = logging.getLogger(__file__)


def as_dict(qrylist):
    out = []
    for qry in qrylist:
       #out.append(model_to_dict(qry,fields=fields,exclude=exclude))
       #obj = qry.first()
        level = getattr(qry, "level")
        dueon = getattr(qry, "due")
        msg = getattr(qry, "message")
        notion="" if level==1 else "IMPORTANT! "
        due_on="" if dueon==None else " Note: Due on "+ dueon.strftime('%b %-d %-I:%M %p')
        out.append({'message': notion+msg+due_on})

    return out


# Create your models here.

class apitest (models.Model):
    """A trial of test API."""
    name= models.CharField(max_length=30,db_index=True,unique=True) #,default=code_generate)
    uid = models.CharField(max_length=100) #ForeignKey(User,db_index=True, on_delete=models.CASCADE)
    gjson=JSONField()
    def __str__(self):
        return "%s_%s" % (self.uid, self.name)

class apiuser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='apiuser',
        on_delete=models.CASCADE)
#   group = models.ForeignKey(Group, on_delete=models.CASCADE)
    last_checked = models.DateTimeField(default=timezone.now, db_index=True)

class Message(models.Model):
    #id= models.AutoField(primary_key=True)
    handle=models.ForeignKey(User, #apiuser --> use apiuser will be deleted if logout (api/signal.py)
        related_name='message', null=True,
        #to_field='user', #'user' --> if use apiuser
        on_delete=models.SET_NULL #CASCADE caused delete if a user have been deleted
    )
    group= models.CharField(max_length=30, default="all")
    #group= models.ForeignKey(Group,
    #    to_field='name',
    #    default='', null=True, blank=True,
    #    on_delete=models.SET_NULL
    #)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    due = models.DateTimeField(default=None, db_index=False, null=True, blank=True)

    class MsgLevel(models.IntegerChoices): # >= Django 3
        NORMAL= 1, _('Normal')
        URGENT= 2, _('Urgent')
        ONTOP = 3, _('Ontop')
    level = models.IntegerField(choices=MsgLevel.choices, default=MsgLevel.NORMAL)

    @staticmethod
    def must_seen(last_checked=timezone.now):
        #q_check = Q(timestamp__gt=last_checked) # timestamp greater than user last_checked
        logger.info('Got a dtime criteria: %s', last_checked)
        qry = Message.objects.filter(
            Q(handle__username='djbioer') &
            (Q(timestamp__gt=last_checked) | (Q(due__isnull=False) & Q(due__gt=timezone.now()) & Q(level__gt=1))) #__date__gt
            ).order_by('timestamp').order_by('-level')
        logger.info('Must Seen: %s', qry)
        qjson = {} if not qry.exists() else as_dict(qry)
        return qjson

    #def __unicode__(self):
    #    return '[{timestamp}] {handle} to {group}: {message}'.format(**self.as_dict())

    #def save(self, *args, **kwargs):
        #if self.pk is None:  # if this is new object (not update)
            #self.msgid += 1
            #self.msguid = str(uuid.uuid4())
    #   instance = super(Message, self).save(*args, **kwargs)
    #   return instance

    #@property
    #def formatted_due(self):
    #    return self.due.strftime('%b %-d %-I:%M %p')

    #def as_dict(self):
    #    return {'message': self.message
    #        'group': self.group,
    #        'level': self.level.value,
    #        'due': self.due,
    #        'timestamp': self.formatted_timestamp}

#class MsgForm(ModelForm):
#    class Meta:
#        model = Message
#        fields = ['handle', 'message', 'group', 'level', 'due', 'timestamp']

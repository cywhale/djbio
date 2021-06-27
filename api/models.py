#from __future__ import unicode_literals
from django.db import models
#from django.forms import ModelForm
#from django.contrib.gis.db import models
from django.contrib.auth.models import Group, User
#from django.db.models import JSONField
# Django 2.2.23
# from django.contrib.postgres.fields import JSONField
# from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField #Django 3.2.3
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import datetime
import json

import logging
logger = logging.getLogger(__file__)


def formmated_msg(message, dueon, level):
    notion="" if level==1 else "IMPORTANT! "
    due_on="" #if dueon==None else " Note: Due on "+ timezone.localtime(dueon).strftime('%Y-%m-%d %H:%M') #'%b %-d %-I:%M %p')
    if dueon is not None:
      if isinstance(dueon, datetime):
         due_on = " Note: Due on "+ timezone.localtime(dueon).strftime('%Y-%m-%d %H:%M') #'%b %-d %-I:%M %p')
      else:
         due_on = " Note: Due on "+ datetime.strptime(dueon, "%Y-%m-%dT%H:%M:%S.%f").strftime('%Y-%m-%d %H:%M')

    return notion+message+due_on

def msg_as_dict(qrylist):
    out = []
    for qry in qrylist:
       #out.append(model_to_dict(qry,fields=fields,exclude=exclude))
       #obj = qry.first()
        level = getattr(qry, "level")
        dueon = getattr(qry, "due")
        msg = getattr(qry, "message")
        #notion="" if level==1 else "IMPORTANT! "
        #due_on="" if dueon==None else " Note: Due on "+ timezone.localtime(dueon).strftime('%Y-%m-%d %H:%M') #'%b %-d %-I:%M %p')
        out.append({'message': formmated_msg(msg, dueon, level)})

    return out

# Create your models here. #Note that timezone.localtime(timestamp/due), otherwise cause an UTC timezone offset (-8)

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
    channel_name = models.CharField(max_length=100, default="") #for build single channel (to single user)
    last_checked = models.DateTimeField(db_index=False, null=True, blank=True) #auto_now=True cannot be updated
    #msg_notseen = ArrayField(models.IntegerField(), null=True, blank=True) #that list removed if user checked close in html

    @property
    def formatted_lastchecked(self):
        tlabel = timezone.localtime(self.last_checked).strftime('%Y-%m-%d %H:%M') if self.last_checked is not None else "(first login)" #('%b %-d %-I:%M %p')
        return tlabel

    def __str__(self):
        return "%s last checked: %s" % (self.user.username, self.formatted_lastchecked)

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
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    due = models.DateTimeField(default=None, db_index=False, null=True, blank=True)

    class MsgLevel(models.IntegerChoices): # >= Django 3
        NORMAL= 1, _('Normal')
        URGENT= 2, _('Urgent')
        ONTOP = 3, _('Ontop')

    level = models.IntegerField(choices=MsgLevel.choices, default=MsgLevel.NORMAL)

    @staticmethod
    def must_seen(last_checked=timezone.now):
        #q_check = Q(timestamp__gt=last_checked) # timestamp greater than user last_checked
        nowt = timezone.localtime(timezone.now())
        chktime = timezone.localtime(last_checked) if last_checked is not None else nowt.replace(hour=0,minute=0,second=0,microsecond=0) #datetime.strptime('1970-01-01 00:00', "%Y-%m-%d %H:%M")
        #logger.info('Got a dtime criteria: %s %s %s', chktime, nowt, timezone.now()) ##Note: timezone.now is a UTC time!!
        qry = Message.objects.filter(
            Q(handle__username='djbioer') &
            (Q(timestamp__gt=chktime) | (Q(due__isnull=False) & Q(due__gt=nowt) & Q(level__gt=1))) #__date__gt
            ).order_by('timestamp').order_by('-level')
        logger.info('Must Seen: %s', qry)
        qjson = {} if not qry.exists() else msg_as_dict(qry)
        return qjson

    #def __unicode__(self): #seems not work in python3
    def __str__(self):
        return '[{timestamp}]{level} {group} {message} {due}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return timezone.localtime(self.timestamp).strftime('%Y-%m-%d %H:%M')

    @property
    def formatted_message(self):
        return formmated_msg(self.message, self.due, self.level)

    def as_dict(self):
        return {'message': self.message,
            'level': '' if self.level==1 else '['+self.get_level_display()+']', # display self.level name
            'group': '' if self.group=='all' else ' to'+self.group+': ',
            'due': "" if self.due==None else " Due on "+ timezone.localtime(self.due).strftime('%Y-%m-%d %H:%M'),
            'timestamp': self.formatted_timestamp}

    #def save(self, *args, **kwargs):
        #if self.pk is None:  # if this is new object (not update)
            #self.msgid += 1
            #self.msguid = str(uuid.uuid4())
        #super(Message, self).save(*args, **kwargs)
        #return self.formatted_message

#class MsgForm(ModelForm):
#    class Meta:
#        model = Message
#        fields = ['handle', 'message', 'group', 'level', 'due', 'timestamp']



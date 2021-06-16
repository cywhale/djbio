from __future__ import unicode_literals

from django.db import models
from django.forms import ModelForm
#from django.contrib.gis.db import models
from django.contrib.auth.models import Group #, User
#from django.db.models import JSONField
# Django 2.2.23
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField #Django 3.2.3
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
    handle=models.ForeignKey(apiuser, #settings.AUTH_USER_MODEL,  #User
        related_name='message',
        to_field='user',
        on_delete=models.CASCADE,
    )
    group= models.CharField(max_length=30, default="all")
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    due = models.DateTimeField(default=timezone.now, db_index=False, null=True, blank=True)

    class MsgLevel(models.IntegerChoices): # >= Django 3
        NORMAL= 1, _('Normal')
        URGENT= 2, _('Urgent')
        ONTOP = 3, _('Ontop')
    level = models.IntegerField(choices=MsgLevel.choices, default=MsgLevel.NORMAL)
    #level = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return '[{timestamp}] {handle} to {group}: {message}'.format(**self.as_dict())

    def save(self, *args, **kwargs):
        #if self.pk is None:  # if this is new object (not update)
            #self.msgid += 1
            #self.msguid = str(uuid.uuid4())
        instance = super(Message, self).save(*args, **kwargs)
        return instance

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {'handle': self.handle, 'message': self.message,
            'group': self.group,
            'level': self.level.value,
            'due': self.due,
            'timestamp': self.formatted_timestamp}

class MsgForm(ModelForm):
    class Meta:
        model = Message
        fields = ['handle', 'message', 'group', 'level', 'due', 'timestamp']

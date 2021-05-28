from django.db import models
#from django.contrib.gis.db import models
#from django.contrib.auth.models import User
#from django.db.models import JSONField
from django.contrib.postgres.fields import JSONField
from django.conf import settings

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

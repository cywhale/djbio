from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from api.models import apiuser

@receiver(user_logged_in)
def on_user_login(sender, **kwargs):
    apiuser.objects.get_or_create(user=kwargs.get('user'))

@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    apiuser.objects.filter(user=kwargs.get('user')).delete()

from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import api.signals

#class apiAdminConfig(AdminConfig):
#    default_site = 'admin.tmptryAdminSite'

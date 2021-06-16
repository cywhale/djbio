from django.contrib import admin

class tmptryAdminSite(admin.AdminSite):
    index_title = 'DjBio'
    title_header = 'django bio admin'
    site_header = 'djbio'
#   logout_template = 'admin/logout_tmptry.html'
    index_template = 'admin/admin_tmptry.html'

# admin_site = tmptryAdminSite(name='api')

# Register your models here.

from .models import *
admin.site.register(apitest) #admin.site, tmp try to customize it to use #admin_site
admin.site.register(apiuser)
admin.site.register(Message)

#admin_site.disable_action('delete_selected')

class apiuserAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_form01.html'

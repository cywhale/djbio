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
#admin.site.register(apitest) #admin.site, tmp try to customize it to use #admin_site
@admin.register(apitest)
@admin.register(apiuser)
@admin.register(Message)

class MessageAdmin(admin.ModelAdmin):
    change_list_template = 'admin/change_list01.html'

#admin_site.disable_action('delete_selected')



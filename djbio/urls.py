"""djbio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin #admin.site, tmp try to customize it
#from api.admin import admin_site
from django.urls import include, path, re_path
from api.djapi import djapi
#import api.views

urlpatterns = [
    #path('admin/', admin_site.urls), #admin.site, tmp try to customize it
    path('admin/', admin.site.urls),
    path('api/', djapi.urls),
    re_path(r'^', include(('api.urls', 'apitest'), namespace='apitest')), #change api-> apitest, api go for django-ninja  #api.views.index
]

#admin.site.index_template = 'admin/admin_tmptry.html'
#admin.autodiscover()

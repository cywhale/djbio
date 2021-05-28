from django.contrib import admin
from django.urls import re_path #, path

from . import views

urlpatterns = [
    re_path(r'^login/$', views.log_in, name='log_in'),
    re_path(r'^logout/$', views.log_out, name='log_out'),
    re_path(r'^signup/$', views.sign_up, name='sign_up'),
    re_path(r'^$', views.user_handler, name='user_handler'),
    re_path(r'^api/$', views.dboard, name='dboard'), #api.views.dboard
]

from django.contrib import admin
from django.urls import re_path #, path

from . import views

urlpatterns = [
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^logout/$', views.logout, name='logout'),
    re_path(r'^signup/$', views.signup, name='signup'),
    re_path(r'^$', views.user, name='user'),
    re_path(r'^api/$', views.dboard, name='dboard'), #api.views.dboard
]

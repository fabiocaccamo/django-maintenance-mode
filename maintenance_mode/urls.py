# -*- coding: utf-8 -*-

from django.conf.urls import url

from maintenance_mode import views


urlpatterns = [
    url(r'^off/$', views.maintenance_mode_off, name='maintenance_mode_off'),
    url(r'^on/$', views.maintenance_mode_on, name='maintenance_mode_on'),
]


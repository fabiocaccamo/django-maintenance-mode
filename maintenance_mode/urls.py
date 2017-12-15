# -*- coding: utf-8 -*-

import django

if django.VERSION < (2, 0):
    from django.conf.urls import url as re_path
else:
    from django.urls import re_path

from maintenance_mode import views


urlpatterns = [
    re_path(r'^off/$', views.maintenance_mode_off, name='maintenance_mode_off'),
    re_path(r'^on/$', views.maintenance_mode_on, name='maintenance_mode_on'),
]

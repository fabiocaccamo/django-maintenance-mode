# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^off/$', 'maintenance_mode.views.maintenance_mode_off', name='maintenance_mode_off'), 
    url(r'^on/$', 'maintenance_mode.views.maintenance_mode_on', name='maintenance_mode_on'), 
)


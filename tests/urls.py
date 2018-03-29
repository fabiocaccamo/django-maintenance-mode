# -*- coding: utf-8 -*-

import django

if django.VERSION < (2, 0):
    from django.conf.urls import include, url as re_path
else:
    from django.urls import include, re_path

from django.http import HttpResponse

from .views import (
    force_maintenance_mode_off_view, ForceMaintenanceModeOffView,
    force_maintenance_mode_on_view, ForceMaintenanceModeOnView, )


urlpatterns = [
    re_path(r'^$',
            lambda x: HttpResponse(),
            name='root'),

    re_path(r'^maintenance-mode-redirect/$',
            lambda x: HttpResponse(),
            name='maintenance_mode_redirect'),

    re_path(r'^maintenance-mode-off-view-func/$',
            force_maintenance_mode_off_view,
            name='maintenance_mode_off_view_func'),

    re_path(r'^maintenance-mode-off-view-class/$',
            ForceMaintenanceModeOffView.as_view(),
            name='maintenance_mode_off_view_class'),

    re_path(r'^maintenance-mode-on-view-func/$',
            force_maintenance_mode_on_view,
            name='maintenance_mode_on_view_func'),

    re_path(r'^maintenance-mode-on-view-class/$',
            ForceMaintenanceModeOnView.as_view(),
            name='maintenance_mode_on_view_class'),

    re_path(r'^maintenance-mode/',
            include('maintenance_mode.urls')),
]

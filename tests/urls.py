# -*- coding: utf-8 -*-

import django

if django.VERSION < (2, 0):
    from django.conf.urls import include, url as re_path
else:
    from django.urls import include, re_path

from django.http import HttpResponse


urlpatterns = [
    re_path(r'^$', lambda x: HttpResponse(), name='root'),
    re_path(r'^maintenance-mode-redirect/$', lambda x: HttpResponse(), name='maintenance_mode_redirect'),
    re_path(r'^maintenance-mode/', include('maintenance_mode.urls')),
]

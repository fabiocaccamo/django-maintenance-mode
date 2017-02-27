# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.http import HttpResponse


urlpatterns = [
    url(r'^$', lambda x: HttpResponse()),
    url(r'^maintenance-mode-redirect/$', lambda x: HttpResponse(), name='maintenance_mode_redirect'),
    url(r'^maintenance-mode/', include('maintenance_mode.urls')),
]


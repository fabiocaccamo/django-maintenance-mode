# -*- coding: utf-8 -*-

import django

if django.VERSION < (2, 0):
    from django.conf.urls import url as re_path
else:
    from django.urls import re_path

from django.http import HttpResponse


urlpatterns = [
    re_path(r'^$', lambda x: HttpResponse()),
]

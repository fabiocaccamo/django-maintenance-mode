# -*- coding: utf-8 -*-

import django

from django.contrib import admin

if django.VERSION < (2, 0):
    from django.conf.urls import url as re_path
else:
    from django.urls import re_path

from django.http import HttpResponse


urlpatterns = [
    re_path(r'^$',
            lambda x: HttpResponse(),
            name='root'),
    re_path(r'^admin/', admin.site.urls),
]

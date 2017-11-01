# -*- coding: utf-8 -*-
import django

if django.VERSION < (1, 10):
    __MaintenanceModeMiddlewareBaseClass = object
else:
    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    from django.utils.deprecation import MiddlewareMixin
    __MaintenanceModeMiddlewareBaseClass = MiddlewareMixin

from maintenance_mode import core
from maintenance_mode.http import get_maintenance_response, is_under_maintenance


class MaintenanceModeMiddleware(__MaintenanceModeMiddlewareBaseClass):

    def process_request(self, request):

        if not core.get_maintenance_mode():
            return None

        if is_under_maintenance(request):
            return get_maintenance_response(request)
        else:
            return None

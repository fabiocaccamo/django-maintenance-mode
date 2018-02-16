# -*- coding: utf-8 -*-

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if django.VERSION < (2, 0):
    from django.core.urlresolvers import NoReverseMatch, resolve, reverse
else:
    from django.urls import NoReverseMatch, resolve, reverse

from django.utils.module_loading import import_string

if django.VERSION < (1, 10):
    __MaintenanceModeMiddlewareBaseClass = object
else:
    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    from django.utils.deprecation import MiddlewareMixin
    __MaintenanceModeMiddlewareBaseClass = MiddlewareMixin

from maintenance_mode import core, utils
from maintenance_mode.http import get_maintenance_response

import re
import sys


class MaintenanceModeMiddleware(__MaintenanceModeMiddlewareBaseClass):

    def process_request(self, request):

        if not core.get_maintenance_mode():
            return None

        try:
            url_off = reverse('maintenance_mode_off')

            resolve(url_off)

            if url_off == request.path_info:
                return None

        except NoReverseMatch:
            # maintenance_mode.urls not added
            pass

        if hasattr(request, 'user'):

            if settings.MAINTENANCE_MODE_IGNORE_STAFF \
                    and request.user.is_staff:
                return None

            if settings.MAINTENANCE_MODE_IGNORE_SUPERUSER \
                    and request.user.is_superuser:
                return None

        if settings.MAINTENANCE_MODE_IGNORE_TESTS:

            is_testing = False

            if (len(sys.argv) > 0 and 'runtests' in sys.argv[0]) \
                    or (len(sys.argv) > 1 and sys.argv[1] == 'test'):
                # python runtests.py | python manage.py test | python
                # setup.py test | django-admin.py test
                is_testing = True

            if is_testing:
                return None

        if settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:

            if settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS:
                try:
                    get_client_ip_address_func = import_string(
                        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS)
                except ImportError:
                    raise ImproperlyConfigured(
                        'settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS '
                        'is not a valid function path.')
                else:
                    client_ip_address = get_client_ip_address_func(request)
            else:
                client_ip_address = utils.get_client_ip_address(request)

            for ip_address in settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:

                ip_address_re = re.compile(ip_address)

                if ip_address_re.match(client_ip_address):
                    return None

        if settings.MAINTENANCE_MODE_IGNORE_URLS:

            for url in settings.MAINTENANCE_MODE_IGNORE_URLS:

                if not isinstance(url, re._pattern_type):
                    url = str(url)
                url_re = re.compile(url)

                if url_re.match(request.path_info):
                    return None

        if settings.MAINTENANCE_MODE_REDIRECT_URL:

            redirect_url_re = re.compile(
                settings.MAINTENANCE_MODE_REDIRECT_URL)

            if redirect_url_re.match(request.path_info):
                return None

        return get_maintenance_response(request)

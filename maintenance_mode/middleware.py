# -*- coding: utf-8 -*-

import django
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, resolve, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.module_loading import import_string

if django.VERSION < (1, 8):
    from django.shortcuts import render_to_response
    from django.template import RequestContext

from django.utils.cache import add_never_cache_headers

if django.VERSION < (1, 10):
    __MaintenanceModeMiddlewareBaseClass = object
else:
    #https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    from django.utils.deprecation import MiddlewareMixin
    __MaintenanceModeMiddlewareBaseClass = MiddlewareMixin

from maintenance_mode import core, settings, utils

import re
import sys


class MaintenanceModeMiddleware(__MaintenanceModeMiddlewareBaseClass):

    def process_request(self, request):

        if settings.MAINTENANCE_MODE or core.get_maintenance_mode():

            try:
                url_off = reverse('maintenance_mode_off')

                resolve(url_off)

                if url_off == request.path_info:
                    return None

            except NoReverseMatch:
                #maintenance_mode.urls not added
                pass

            if hasattr(request, 'user'):

                if settings.MAINTENANCE_MODE_IGNORE_STAFF and request.user.is_staff:
                    return None

                if settings.MAINTENANCE_MODE_IGNORE_SUPERUSER and request.user.is_superuser:
                    return None

                if settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS and request.user.is_anonymous():
                    return None

            if settings.MAINTENANCE_MODE_IGNORE_TESTS:

                is_testing = False

                if (len(sys.argv) > 0 and 'runtests' in sys.argv[0]) or (len(sys.argv) > 1 and sys.argv[1] == 'test'):
                    #python runtests.py | python manage.py test | python setup.py test | django-admin.py test
                    is_testing = True

                if is_testing:
                    return None

            if settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:

                if settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS:
                    try:
                        get_client_ip_address_func = import_string(settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS)
                    except ImportError:
                        raise ImproperlyConfigured(
                            'settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS is not a valid function path.')
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

                    url_re = re.compile(url)

                    if url_re.match(request.path_info):
                        return None

            if settings.MAINTENANCE_MODE_REDIRECT_URL:

                redirect_url_re = re.compile(settings.MAINTENANCE_MODE_REDIRECT_URL)

                if redirect_url_re.match(request.path_info):
                    return None

                return HttpResponseRedirect(settings.MAINTENANCE_MODE_REDIRECT_URL)

            else:

                request_context = {}

                if settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT:
                    try:
                        get_request_context_func = import_string(settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT)
                    except ImportError:
                        raise ImproperlyConfigured(
                            'settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT is not a valid function path.')
                    else:
                        request_context = get_request_context_func(request=request)

                if django.VERSION < (1, 8):
                    response = render_to_response(settings.MAINTENANCE_MODE_TEMPLATE, request_context, context_instance=RequestContext(request), content_type='text/html')
                else:
                    response = render(request, settings.MAINTENANCE_MODE_TEMPLATE, context=request_context, content_type='text/html', status=503)

                add_never_cache_headers(response)
                return response
        else:
            return None


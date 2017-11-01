# -*- coding: utf-8 -*-

"""HTTP response utilities."""
import sys
import re

import django
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, resolve, reverse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_string

from maintenance_mode import settings

from .utils import get_client_ip_address


def is_under_maintenance(request):
    """Return whether the request is under maintenance."""
    # Check if the request targets the maintenance view itself.
    try:
        url_off = reverse('maintenance_mode_off')
        resolve(url_off)
        if url_off == request.path_info:
            return False
    except NoReverseMatch:
        pass

    # Check if user is allowed to bypass maintenance.
    if hasattr(request, 'user'):
        if settings.MAINTENANCE_MODE_IGNORE_STAFF and request.user.is_staff:
            return False
        if settings.MAINTENANCE_MODE_IGNORE_SUPERUSER and request.user.is_superuser:
            return False

    # Check if maintenance is disabled for tests.
    if settings.MAINTENANCE_MODE_IGNORE_TESTS:
        is_testing = False
        if (len(sys.argv) > 0 and 'runtests' in sys.argv[0]) or (len(sys.argv) > 1 and sys.argv[1] == 'test'):
            # python runtests.py | python manage.py test | python
            # setup.py test | django-admin.py test
            is_testing = True
        if is_testing:
            return False

    # Check if the client (IP address) is allowed to bypass the maintenance.
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
            client_ip_address = get_client_ip_address(request)
        for ip_address in settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:
            ip_address_re = re.compile(ip_address)
            if ip_address_re.match(client_ip_address):
                return False

    # Check if the URL is excluded from maintenance mode.
    if settings.MAINTENANCE_MODE_IGNORE_URLS:
        for url in settings.MAINTENANCE_MODE_IGNORE_URLS:
            url_re = re.compile(url)
            if url_re.match(request.path_info):
                return False

    # Check if the URL displays the maintenance page.
    if settings.MAINTENANCE_MODE_REDIRECT_URL:
        redirect_url_re = re.compile(settings.MAINTENANCE_MODE_REDIRECT_URL)
        if redirect_url_re.match(request.path_info):
            return False

    # Otherwise the request is under maintenance
    return True


def get_maintenance_response(request):
    """Return a maintenance response."""
    if settings.MAINTENANCE_MODE_REDIRECT_URL:
        return redirect(settings.MAINTENANCE_MODE_REDIRECT_URL)

    context = {}

    if settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT:
        try:
            get_request_context_func = import_string(
                settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT)
        except ImportError:
            raise ImproperlyConfigured(
                'settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT '
                'is not a valid function path.'
            )

        context = get_request_context_func(request=request)

    if django.VERSION < (1, 8):
        kwargs = {'context_instance': RequestContext(request, context)}
    else:
        kwargs = {'context': context}

    response = render(request, settings.MAINTENANCE_MODE_TEMPLATE,
                      content_type='text/html', status=503, **kwargs)

    add_never_cache_headers(response)
    return response

# -*- coding: utf-8 -*-

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if django.VERSION < (2, 0):
    from django.core.urlresolvers import (
        NoReverseMatch, resolve, Resolver404, reverse, )
else:
    from django.urls import (
        NoReverseMatch, resolve, Resolver404, reverse, )

from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_string

from maintenance_mode.core import get_maintenance_mode
from maintenance_mode.utils import get_client_ip_address

import re
import sys


def get_maintenance_response(request):
    """
    Return a '503 Service Unavailable' maintenance response.
    """
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


def need_maintenance_response(request):
    """
    Tells if the given request needs a maintenance response or not.
    """

    try:
        view_match = resolve(request.path)
        view_func = view_match[0]
        view_dict = view_func.__dict__

        view_force_maintenance_mode_off = view_dict.get(
            'force_maintenance_mode_off', False)
        if view_force_maintenance_mode_off:
            # view has 'force_maintenance_mode_off' decorator
            return False

        view_force_maintenance_mode_on = view_dict.get(
            'force_maintenance_mode_on', False)
        if view_force_maintenance_mode_on:
            # view has 'force_maintenance_mode_on' decorator
            return True

    except Resolver404:
        pass

    if not get_maintenance_mode():
        return False

    try:
        url_off = reverse('maintenance_mode_off')

        resolve(url_off)

        if url_off == request.path_info:
            return False

    except NoReverseMatch:
        # maintenance_mode.urls not added
        pass

    if hasattr(request, 'user'):

        if django.VERSION < (1, 10):
            if settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER \
                    and request.user.is_anonymous():
                return False

            if settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER \
                    and request.user.is_authenticated():
                return False
        else:
            if settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER \
                    and request.user.is_anonymous:
                return False

            if settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER \
                    and request.user.is_authenticated:
                return False

        if settings.MAINTENANCE_MODE_IGNORE_STAFF \
                and request.user.is_staff:
            return False

        if settings.MAINTENANCE_MODE_IGNORE_SUPERUSER \
                and request.user.is_superuser:
            return False

    if settings.MAINTENANCE_MODE_IGNORE_TESTS:

        is_testing = False

        if (len(sys.argv) > 0 and 'runtests' in sys.argv[0]) \
                or (len(sys.argv) > 1 and sys.argv[1] == 'test'):
            # python runtests.py | python manage.py test | python
            # setup.py test | django-admin.py test
            is_testing = True

        if is_testing:
            return False

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
            client_ip_address = get_client_ip_address(request)

        for ip_address in settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:

            ip_address_re = re.compile(ip_address)

            if ip_address_re.match(client_ip_address):
                return False

    if settings.MAINTENANCE_MODE_IGNORE_URLS:

        for url in settings.MAINTENANCE_MODE_IGNORE_URLS:

            if not isinstance(url, re._pattern_type):
                url = str(url)
            url_re = re.compile(url)

            if url_re.match(request.path_info):
                return False

    if settings.MAINTENANCE_MODE_REDIRECT_URL:

        redirect_url_re = re.compile(
            settings.MAINTENANCE_MODE_REDIRECT_URL)

        if redirect_url_re.match(request.path_info):
            return False

    return True

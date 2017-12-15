# -*- coding: utf-8 -*-

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_string


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

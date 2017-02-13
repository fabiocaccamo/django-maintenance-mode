# -*- coding: utf-8 -*-

import django
from django.core.urlresolvers import NoReverseMatch, resolve, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

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

from maintenance_mode import core
from maintenance_mode import settings


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

            for ip_address_re in settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES_RE:

                if ip_address_re.match(request.META['REMOTE_ADDR']):
                    return None

            for url_re in settings.MAINTENANCE_MODE_IGNORE_URLS_RE:

                if url_re.match(request.path_info):
                    return None

            if settings.MAINTENANCE_MODE_REDIRECT_URL:
                return HttpResponseRedirect(settings.MAINTENANCE_MODE_REDIRECT_URL)
            else:
                if django.VERSION < (1, 8):
                    response = render_to_response(settings.MAINTENANCE_MODE_TEMPLATE, self.get_request_context(request), context_instance=RequestContext(request), content_type='text/html')
                else:
                    response = render(request, settings.MAINTENANCE_MODE_TEMPLATE, context=self.get_request_context(request), content_type='text/html', status=503)

                add_never_cache_headers(response)
                return response
        else:
            return None


    def get_request_context(self, request):

        if settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT:

            from importlib import import_module

            func_path = settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT
            mod_name, func_name = func_path.rsplit('.',1)
            mod = import_module(mod_name)
            func = getattr(mod, func_name)

            return func(request = request)
        else:
            return {}


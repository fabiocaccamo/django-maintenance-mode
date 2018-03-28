# -*- coding: utf-8 -*-

import django
from django.http import HttpResponse
from django.utils.decorators import method_decorator

if django.VERSION < (1, 10):
    from django.views.generic import View
else:
    from django.views import View

from maintenance_mode.decorators import ignore_maintenance_mode


@ignore_maintenance_mode
def maintenance_mode_ignore(request):
    return HttpResponse()


class MaintenanceModeIgnoreView(View):

    @method_decorator(ignore_maintenance_mode)
    def dispatch(self, *args, **kwargs):
        return super(MaintenanceModeIgnoreView, self).dispatch(*args, **kwargs)

    def get(self, request):
        return HttpResponse()

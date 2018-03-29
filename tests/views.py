# -*- coding: utf-8 -*-

import django
from django.http import HttpResponse
from django.utils.decorators import method_decorator

if django.VERSION < (1, 10):
    from django.views.generic import View
else:
    from django.views import View

from maintenance_mode.decorators import (
    force_maintenance_mode_off, force_maintenance_mode_on, )


@force_maintenance_mode_off
def force_maintenance_mode_off_view(request):
    return HttpResponse()


@force_maintenance_mode_on
def force_maintenance_mode_on_view(request):
    return HttpResponse()


class ForceMaintenanceModeOffView(View):

    @method_decorator(force_maintenance_mode_off)
    def dispatch(self, *args, **kwargs):
        return super(ForceMaintenanceModeOffView, self).dispatch(*args, **kwargs)

    def get(self, request):
        return HttpResponse()


class ForceMaintenanceModeOnView(View):

    @method_decorator(force_maintenance_mode_on)
    def dispatch(self, *args, **kwargs):
        return super(ForceMaintenanceModeOnView, self).dispatch(*args, **kwargs)

    def get(self, request):
        return HttpResponse()

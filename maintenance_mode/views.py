# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect

from maintenance_mode.core import set_maintenance_mode


def maintenance_mode_off(request):
    """
    Deactivate maintenance-mode and redirect to site root.
    Only superusers are allowed to use this view.
    """
    if request.user.is_superuser:
        set_maintenance_mode(False)

    return HttpResponseRedirect('/')


def maintenance_mode_on(request):
    """
    Activate maintenance-mode and redirect to site root.
    Only superusers are allowed to use this view.
    """
    if request.user.is_superuser:
        set_maintenance_mode(True)

    return HttpResponseRedirect('/')

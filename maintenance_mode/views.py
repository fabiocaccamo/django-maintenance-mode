# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect

from maintenance_mode import core


def maintenance_mode_off(request):

    if request.user.is_superuser:

        core.set_maintenance_mode(False)

    return HttpResponseRedirect('/')


def maintenance_mode_on(request):

    if request.user.is_superuser:

        core.set_maintenance_mode(True)

    return HttpResponseRedirect('/')


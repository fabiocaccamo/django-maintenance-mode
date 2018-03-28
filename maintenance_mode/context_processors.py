# -*- coding: utf-8 -*-

from maintenance_mode.core import get_maintenance_mode


def maintenance_mode(request):
    return { 'maintenance_mode':get_maintenance_mode() }

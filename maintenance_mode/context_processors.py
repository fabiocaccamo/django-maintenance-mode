# -*- coding: utf-8 -*-

from maintenance_mode.core import get_maintenance_mode, get_maintenance_mode_up_time


def maintenance_mode(request):
    return { 'maintenance_mode':get_maintenance_mode(),
             'maintenance_mode_up_time': get_maintenance_mode_up_time() }

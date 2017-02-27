# -*- coding: utf-8 -*-

from maintenance_mode import core


def maintenance_mode(request):
    return { 'maintenance_mode':core.get_maintenance_mode() }


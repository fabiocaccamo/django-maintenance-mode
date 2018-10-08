# -*- coding: utf-8 -*-

from functools import wraps

from maintenance_mode.http import get_maintenance_response


def force_maintenance_mode_off(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrapper.__dict__['force_maintenance_mode_off'] = True
    return wrapper


def force_maintenance_mode_on(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return get_maintenance_response(request)
    wrapper.__dict__['force_maintenance_mode_on'] = True
    return wrapper

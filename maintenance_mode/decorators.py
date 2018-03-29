# -*- coding: utf-8 -*-

from maintenance_mode.http import get_maintenance_response


def force_maintenance_mode_off(view_func):
    def wrap(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrap.__dict__['force_maintenance_mode_off'] = True
    wrap.__doc__ = view_func.__doc__
    wrap.__name__ = view_func.__name__
    return wrap


def force_maintenance_mode_on(view_func):
    def wrap(request, *args, **kwargs):
        return get_maintenance_response(request)
    wrap.__dict__['force_maintenance_mode_on'] = True
    wrap.__doc__ = view_func.__doc__
    wrap.__name__ = view_func.__name__
    return wrap

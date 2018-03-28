# -*- coding: utf-8 -*-


def ignore_maintenance_mode(view_func):
    view_func.__dict__['ignore_maintenance_mode'] = True
    return view_func

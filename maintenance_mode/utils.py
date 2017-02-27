# -*- coding: utf-8 -*-

from importlib import import_module


def import_function( path ):

    func_path = path
    mod_name, func_name = func_path.rsplit('.', 1)

    if mod_name and func_name:

        try:
            mod = import_module(mod_name)

            try:
                func = getattr(mod, func_name)

                if hasattr(func, '__call__'):
                    return func

            except AttributeError:
                pass

        except ImportError:
            pass

    return None


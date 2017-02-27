# -*- coding: utf-8 -*-

from maintenance_mode import io, settings


def get_maintenance_mode():

    value = io.read_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH)
    value = bool(int(value))
    return value


def set_maintenance_mode(value):

    if not isinstance(value, bool):
        raise TypeError('value argument type is not boolean')

    value = str(int(value))
    io.write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, value)


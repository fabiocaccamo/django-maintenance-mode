# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from maintenance_mode.io import read_file, write_file


def get_maintenance_mode():
    """
    Get maintenance_mode state from state file.
    """

    # If maintenance mode is defined in settings, it has priority.
    if settings.MAINTENANCE_MODE is not None:
        return settings.MAINTENANCE_MODE

    value = read_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, '0')

    if value not in ['0', '1']:
        raise ValueError('state file content value is not 0|1')

    value = bool(int(value))
    return value


def set_maintenance_mode(value):
    """
    Set maintenance_mode state to state file.
    """

    # If maintenance mode is defined in settings, it can't be changed.
    if settings.MAINTENANCE_MODE is not None:
        raise ImproperlyConfigured(
            'Maintenance mode cannot be set dynamically ' \
            'if defined in settings.')

    if not isinstance(value, bool):
        raise TypeError('value argument type is not boolean')

    value = str(int(value))
    write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, value)

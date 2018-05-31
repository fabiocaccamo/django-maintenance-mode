# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from django.utils.decorators import ContextDecorator
except ImportError:
    # ContextDecorator was introduced in Django 1.8
    from django.utils.decorators import available_attrs

    class ContextDecorator(object):
        """A base class that enables a context manager to also be used as a decorator."""

        def __call__(self, func):
            @wraps(func, assigned=available_attrs(func))
            def inner(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)
            return inner

from functools import wraps

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


class override_maintenance_mode(ContextDecorator):
    """Decorator/context manager to locally override a maintenance mode.

    @ivar value: Overriden value of maintenance mode
    @ivar old_value: Original value of maintenance mode
    """
    def __init__(self, value):
        self.value = value
        self.old_value = None

    def __enter__(self):
        self.old_value = get_maintenance_mode()
        set_maintenance_mode(self.value)

    def __exit__(self, exc_type, exc_value, traceback):
        set_maintenance_mode(self.old_value)

from contextlib import ContextDecorator
from functools import wraps

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from maintenance_mode.backends import AbstractStateBackend


def get_maintenance_mode_backend():
    try:
        backend_class = import_string(settings.MAINTENANCE_MODE_STATE_BACKEND)
        if (
            issubclass(backend_class, AbstractStateBackend)
            and backend_class != AbstractStateBackend
        ):
            backend = backend_class()
            return backend
        else:
            raise ImproperlyConfigured(
                "backend doesn't extend "
                "'maintenance_mode.backends.AbstractStateBackend' class."
            )
    except ImportError:
        raise ImproperlyConfigured(
            "backend not found, check "
            "'settings.MAINTENANCE_MODE_STATE_BACKEND' path."
        )


def get_maintenance_mode():
    """
    Get maintenance_mode state from state file.
    """

    # If maintenance mode is defined in settings, it has priority.
    if settings.MAINTENANCE_MODE is not None:
        return settings.MAINTENANCE_MODE

    backend = get_maintenance_mode_backend()
    return backend.get_value()


def set_maintenance_mode(value):
    """
    Set maintenance_mode state to state file.
    """

    # If maintenance mode is defined in settings, it can't be changed.
    if settings.MAINTENANCE_MODE is not None:
        raise ImproperlyConfigured(
            "Maintenance mode cannot be set dynamically " "if defined in settings."
        )

    if not isinstance(value, bool):
        raise TypeError("value argument type is not boolean")

    backend = get_maintenance_mode_backend()
    backend.set_value(value)


class override_maintenance_mode(ContextDecorator):
    """
    Decorator/context manager to locally override a maintenance mode.

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


class maintenance_mode_on(override_maintenance_mode):
    """
    Decorator/context manager to locally set maintenance mode to True.
    """

    def __init__(self):
        super(maintenance_mode_on, self).__init__(True)


class maintenance_mode_off(override_maintenance_mode):
    """
    Decorator/context manager to locally set maintenance mode to False.
    """

    def __init__(self):
        super(maintenance_mode_off, self).__init__(False)

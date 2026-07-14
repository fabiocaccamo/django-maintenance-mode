from contextlib import ContextDecorator

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from maintenance_mode.backends import AbstractStateBackend
from maintenance_mode.utils import get_now_datetime, parse_aware_datetime


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
    except ImportError as error:
        raise ImproperlyConfigured(
            "backend not found, check 'settings.MAINTENANCE_MODE_STATE_BACKEND' path."
        ) from error


def _get_maintenance_mode_by_schedule(state):
    """
    Evaluate a schedule state ({"start": ..., "end": ...})
    against the current datetime.
    """
    start = parse_aware_datetime(state.get("start"))
    end = parse_aware_datetime(state.get("end"))
    now = get_now_datetime()
    started = start is None or start <= now
    ended = end is not None and end <= now
    return started and not ended


def get_maintenance_mode():
    """
    Get maintenance_mode state from state file.
    """

    # If maintenance mode is defined in settings, it has priority.
    if settings.MAINTENANCE_MODE is not None:
        return settings.MAINTENANCE_MODE

    backend = get_maintenance_mode_backend()
    value = backend.get_value()
    if isinstance(value, dict):
        value = _get_maintenance_mode_by_schedule(value)
    return value


def set_maintenance_mode(value, start=None, end=None):
    """
    Set maintenance_mode state to state file,
    optionally scheduled with start and/or end datetimes
    (datetime objects or ISO 8601 strings).
    """

    # If maintenance mode is defined in settings, it can't be changed.
    if settings.MAINTENANCE_MODE is not None:
        raise ImproperlyConfigured(
            "Maintenance mode cannot be set dynamically if defined in settings."
        )

    if not isinstance(value, bool):
        raise TypeError("value argument type is not boolean")

    if start is not None or end is not None:
        if value is not True:
            raise ValueError("start / end arguments can only be used with value True")
        start = parse_aware_datetime(start)
        end = parse_aware_datetime(end)
        if start is not None and end is not None and start >= end:
            raise ValueError("start argument value must be < end argument value")
        if end is not None and end <= get_now_datetime():
            raise ValueError("end argument value must be in the future")
        value = {
            "start": start.isoformat() if start else None,
            "end": end.isoformat() if end else None,
        }

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
        backend = get_maintenance_mode_backend()
        self.old_value = backend.get_value()
        set_maintenance_mode(self.value)

    def __exit__(self, exc_type, exc_value, traceback):
        backend = get_maintenance_mode_backend()
        backend.set_value(self.old_value)


class maintenance_mode_on(override_maintenance_mode):
    """
    Decorator/context manager to locally set maintenance mode to True.
    """

    def __init__(self):
        super().__init__(True)


class maintenance_mode_off(override_maintenance_mode):
    """
    Decorator/context manager to locally set maintenance mode to False.
    """

    def __init__(self):
        super().__init__(False)

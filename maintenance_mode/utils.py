from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.module_loading import import_string


def get_client_ip_address(request):
    """
    Get the client IP Address.
    """
    return request.META["REMOTE_ADDR"]


def get_now_datetime():
    """
    Get the current datetime as an aware datetime object.
    """
    now = timezone.now()
    if timezone.is_naive(now):
        # with USE_TZ = False timezone.now() returns a naive datetime
        now = timezone.make_aware(now)
    return now


def import_function(function_path, setting_name):
    """
    Import a function from its path and
    raise ImproperlyConfigured if the path is invalid
    or the imported object is not callable.
    """
    try:
        function = import_string(function_path)
    except ImportError as error:
        raise ImproperlyConfigured(
            f"settings.{setting_name} is not a valid function path."
        ) from error
    if not callable(function):
        raise ImproperlyConfigured(f"settings.{setting_name} is not a function.")
    return function


def parse_aware_datetime(value):
    """
    Parse a datetime value (datetime object, ISO 8601 string or None)
    and return an aware datetime object (or None).
    """
    if value is None:
        return None
    if isinstance(value, str):
        parsed_value = parse_datetime(value)
        if parsed_value is None:
            raise ValueError(f"Invalid datetime value: {value!r}")
        value = parsed_value
    if not isinstance(value, datetime):
        raise TypeError(
            f"Datetime value type is not datetime | str | None: {type(value).__name__}"
        )
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    return value

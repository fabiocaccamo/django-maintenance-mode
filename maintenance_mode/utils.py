from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


def get_client_ip_address(request):
    """
    Get the client IP Address.
    """
    return request.META["REMOTE_ADDR"]


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

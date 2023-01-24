from django.core.exceptions import ImproperlyConfigured

try:
    from maintenance_mode import settings  # noqa: F401
except ImproperlyConfigured:
    pass

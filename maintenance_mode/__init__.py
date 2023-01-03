from django.core.exceptions import ImproperlyConfigured

try:
    from maintenance_mode import settings
except ImproperlyConfigured:
    pass

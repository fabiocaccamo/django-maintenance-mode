import builtins
from importlib import reload
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured

from .base import MaintenanceModeTestCase


class PackageTestCase(MaintenanceModeTestCase):
    def test_package_import_with_improperly_configured_settings(self):
        import maintenance_mode

        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "maintenance_mode" and fromlist and "settings" in fromlist:
                raise ImproperlyConfigured("Settings are not configured.")
            return real_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", fake_import):
            reload(maintenance_mode)

        reload(maintenance_mode)

from unittest.mock import patch

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.test import override_settings

from maintenance_mode import core, io

from .base import MaintenanceModeTestCase


class BackendsTestCase(MaintenanceModeTestCase):
    def test_backend_local_file(self):
        self._reset_state()

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

    def test_backend_schedule_state(self):
        self._reset_state()

        backend = core.get_maintenance_mode_backend()
        state = {"start": None, "end": "2026-07-14T03:00:00+00:00"}
        backend.set_value(state)
        self.assertEqual(backend.get_value(), state)

        # plain bool state still works after a schedule state
        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

    def test_backend_schedule_state_invalid_values(self):
        self._reset_state()

        backend = core.get_maintenance_mode_backend()

        # invalid schedule state values
        self.assertRaises(ValueError, backend.set_value, {})
        self.assertRaises(ValueError, backend.set_value, {"invalid-key": "1"})
        self.assertRaises(ValueError, backend.set_value, {"start": None, "end": None})

        # invalid schedule state values read from the state file
        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        io.write_file(file_path, "{}")
        self.assertRaises(ValueError, backend.get_value)
        io.write_file(file_path, '{"invalid-key": "1"}')
        self.assertRaises(ValueError, backend.get_value)

        # bool-only serialization methods don't support schedule state
        self.assertRaises(
            ValueError,
            backend.from_bool_to_str_value,
            {"start": None, "end": "2026-07-14T03:00:00+00:00"},
        )

    def test_backend_local_file_invalid_values(self):
        self._reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        io.write_file(file_path, "test")
        backend = core.get_maintenance_mode_backend()
        self.assertRaises(ValueError, backend.get_value)
        self.assertRaises(ValueError, backend.set_value, 2)
        self.assertRaises(ValueError, backend.set_value, "test")

    def test_backend_default_storage(self):
        self._reset_state()

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.DefaultStorageBackend"
        )

        # remove possible state file leftover from previous test runs
        # to ensure the "state file doesn't exist" branch is covered
        default_storage.delete(settings.MAINTENANCE_MODE_STATE_FILE_NAME)

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.LocalFileBackend"
        )

    def test_backend_static_storage(self):
        self._reset_state()

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.StaticStorageBackend"
        )
        settings.STATIC_URL = "/static/"
        settings.STATIC_ROOT = "static"

        # remove possible state file leftover from previous test runs
        # to ensure the "state file doesn't exist" branch is covered
        # (deferred import because staticfiles_storage setup requires STATIC_URL)
        from django.contrib.staticfiles.storage import staticfiles_storage

        staticfiles_storage.delete(settings.MAINTENANCE_MODE_STATE_FILE_NAME)

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.LocalFileBackend"
        )

    def test_backend_cache(self):
        self._reset_state()

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.CacheBackend"
        )
        settings.CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "default",
            }
        }

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

        # test with default MAINTENANCE_MODE_STATE_BACKEND_FALLBACK_VALUE setting
        with patch("maintenance_mode.backends.cache") as mock_cache:
            mock_cache.get.side_effect = Exception
            mock_cache.set.side_effect = Exception
            backend.set_value(False)
            self.assertEqual(backend.get_value(), False)

        # test with MAINTENANCE_MODE_STATE_BACKEND_FALLBACK_VALUE set to True
        settings.MAINTENANCE_MODE_STATE_BACKEND_FALLBACK_VALUE = True
        with patch("maintenance_mode.backends.cache") as mock_cache:
            mock_cache.get.side_effect = Exception
            mock_cache.set.side_effect = Exception
            backend.set_value(False)
            self.assertEqual(backend.get_value(), True)

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.LocalFileBackend"
        )

    def test_backend_cache_with_named_cache(self):
        self._reset_state()

        with override_settings(
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                    "LOCATION": "default",
                },
                "my_custom_cache": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                    "LOCATION": "my_custom_cache",
                },
            },
            MAINTENANCE_MODE_STATE_BACKEND="maintenance_mode.backends.CacheBackend",
            MAINTENANCE_MODE_CACHE_BACKEND="my_custom_cache",
        ):
            backend = core.get_maintenance_mode_backend()

            # Pre-populate the two caches with opposite values so that any
            # accidental read from the default cache would produce the wrong result.
            caches["default"].set("maintenance_mode", "1")
            caches["my_custom_cache"].set("maintenance_mode", "0")

            # get_value must read from the named cache (False), not default (True)
            self.assertEqual(backend.get_value(), False)

            # set_value must write to the named cache only
            backend.set_value(True)
            self.assertEqual(caches["my_custom_cache"].get("maintenance_mode"), "1")
            # default cache must remain unchanged
            self.assertEqual(caches["default"].get("maintenance_mode"), "1")

    def test_backend_cache_with_invalid_named_cache(self):
        self._reset_state()

        with override_settings(
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                    "LOCATION": "default",
                },
            },
            MAINTENANCE_MODE_STATE_BACKEND="maintenance_mode.backends.CacheBackend",
            MAINTENANCE_MODE_CACHE_BACKEND="non_existent_cache",
        ):
            backend = core.get_maintenance_mode_backend()
            self.assertRaises(ImproperlyConfigured, backend.get_value)
            self.assertRaises(ImproperlyConfigured, backend.set_value, False)

    def test_backend_custom_invalid(self):
        self._reset_state()

        backend = settings.MAINTENANCE_MODE_STATE_BACKEND

        # invalid module import
        settings.MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.NoBackend"
        self.assertRaises(ImproperlyConfigured, core.get_maintenance_mode_backend)

        # invalid module type (abstract base class)
        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.middleware.AbstractStateBackend"
        )
        self.assertRaises(ImproperlyConfigured, core.get_maintenance_mode_backend)

        # invalid implementation (methods not implemented)
        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "tests.functions.NotImplementedBackend"
        )
        self.assertRaises(
            NotImplementedError, core.get_maintenance_mode_backend().get_value
        )
        self.assertRaises(
            NotImplementedError, core.get_maintenance_mode_backend().set_value, 0
        )

        # invalid module type
        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.middleware.MaintenanceModeMiddleware"
        )
        self.assertRaises(ImproperlyConfigured, core.get_maintenance_mode_backend)

        settings.MAINTENANCE_MODE_STATE_BACKEND = backend

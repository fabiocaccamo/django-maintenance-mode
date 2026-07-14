import os
from datetime import datetime, timedelta
from tempfile import mkstemp

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from maintenance_mode import core, io

from .base import MaintenanceModeTestCase


class CoreTestCase(MaintenanceModeTestCase):
    def test_core(self):
        self._reset_state()

        core.set_maintenance_mode(True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        core.set_maintenance_mode(False)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_core_invalid_file_path(self):
        self._reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        settings.MAINTENANCE_MODE_STATE_FILE_PATH = self.invalid_file_path

        self.assertRaises((IOError, OSError), core.get_maintenance_mode)
        self.assertRaises((IOError, OSError), core.set_maintenance_mode, True)

        settings.MAINTENANCE_MODE_STATE_FILE_PATH = file_path

    def test_core_maintenance_enabled(self):
        self._reset_state()

        core.set_maintenance_mode(False)
        settings.MAINTENANCE_MODE = True
        val = core.get_maintenance_mode()
        self.assertTrue(val)

    def test_core_maintenance_disabled(self):
        self._reset_state()

        core.set_maintenance_mode(True)
        settings.MAINTENANCE_MODE = False
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_core_set_disabled(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        self.assertRaises(ImproperlyConfigured, core.set_maintenance_mode, True)

    def test_core_invalid_argument(self):
        self._reset_state()

        io.write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, "not bool")
        self.assertRaises(ValueError, core.get_maintenance_mode)
        self.assertRaises(TypeError, core.set_maintenance_mode, "not bool")

    def test_core_schedule(self):
        self._reset_state()

        one_hour = timedelta(hours=1)

        # active schedule (started, not ended)
        core.set_maintenance_mode(
            True, start=timezone.now() - one_hour, end=timezone.now() + one_hour
        )
        self.assertTrue(core.get_maintenance_mode())

        # future schedule (not started yet)
        core.set_maintenance_mode(True, start=timezone.now() + one_hour)
        self.assertFalse(core.get_maintenance_mode())

        # expired schedule (already ended, written directly to the state file)
        backend = core.get_maintenance_mode_backend()
        backend.set_value(
            {"start": None, "end": (timezone.now() - one_hour).isoformat()}
        )
        self.assertFalse(core.get_maintenance_mode())

        # started, end unlimited
        core.set_maintenance_mode(True, start=timezone.now() - one_hour)
        self.assertTrue(core.get_maintenance_mode())

        # start unlimited, not ended
        core.set_maintenance_mode(True, end=timezone.now() + one_hour)
        self.assertTrue(core.get_maintenance_mode())

        # ISO 8601 strings support
        start_str = (timezone.now() - one_hour).isoformat()
        end_str = (timezone.now() + one_hour).isoformat()
        core.set_maintenance_mode(True, start=start_str, end=end_str)
        self.assertTrue(core.get_maintenance_mode())

        # naive datetimes support
        core.set_maintenance_mode(
            True,
            start=datetime.now() - one_hour,
            end=datetime.now() + one_hour,
        )
        self.assertTrue(core.get_maintenance_mode())

        # last-write-wins: plain values overwrite the schedule
        core.set_maintenance_mode(True, end=timezone.now() + one_hour)
        core.set_maintenance_mode(False)
        self.assertFalse(core.get_maintenance_mode())

    def test_core_schedule_invalid_arguments(self):
        self._reset_state()

        one_hour = timedelta(hours=1)

        # schedule with value False
        self.assertRaises(
            ValueError,
            core.set_maintenance_mode,
            False,
            end=timezone.now() + one_hour,
        )

        # start >= end
        self.assertRaises(
            ValueError,
            core.set_maintenance_mode,
            True,
            start=timezone.now() + one_hour,
            end=timezone.now() - one_hour,
        )

        # end in the past
        self.assertRaises(
            ValueError,
            core.set_maintenance_mode,
            True,
            end=timezone.now() - one_hour,
        )

        # invalid datetime string
        self.assertRaises(
            ValueError, core.set_maintenance_mode, True, end="not-a-datetime"
        )

        # invalid datetime type
        self.assertRaises(TypeError, core.set_maintenance_mode, True, end=True)

    def test_core_schedule_override(self):
        self._reset_state()

        one_hour = timedelta(hours=1)

        # override preserves the schedule state
        core.set_maintenance_mode(True, end=timezone.now() + one_hour)
        with core.override_maintenance_mode(False):
            self.assertFalse(core.get_maintenance_mode())
        self.assertTrue(core.get_maintenance_mode())
        backend = core.get_maintenance_mode_backend()
        self.assertIsInstance(backend.get_value(), dict)

    @override_settings(USE_TZ=False)
    def test_core_schedule_without_use_tz(self):
        self._reset_state()

        one_hour = timedelta(hours=1)

        core.set_maintenance_mode(
            True, start=datetime.now() - one_hour, end=datetime.now() + one_hour
        )
        self.assertTrue(core.get_maintenance_mode())

        backend = core.get_maintenance_mode_backend()
        backend.set_value(
            {"start": None, "end": (timezone.now() - one_hour).isoformat()}
        )
        self.assertFalse(core.get_maintenance_mode())


class TestOverrideMaintenanceMode(SimpleTestCase):
    """
    Test `override_maintenance_mode` decorator/context manager.
    """

    def setUp(self):
        dummy, self.tmp_dir = mkstemp()

    def tearDown(self):
        os.remove(self.tmp_dir)

    override_cases = (
        # Maintenance mode states: (environ, override, result)
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, False),
    )

    def test_context_manager_override(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for environ, override, result in self.override_cases:
                core.set_maintenance_mode(environ)
                with core.override_maintenance_mode(override):
                    self.assertEqual(core.get_maintenance_mode(), result)
                self.assertEqual(core.get_maintenance_mode(), environ)

    def test_decorator(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for environ, override, result in self.override_cases:
                core.set_maintenance_mode(environ)

                @core.override_maintenance_mode(override)
                def test_function():
                    self.assertEqual(core.get_maintenance_mode(), result)  # noqa: B023

                test_function()

    def test_context_manager_on(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for value in [True, False]:
                core.set_maintenance_mode(value)
                with core.maintenance_mode_on():
                    self.assertEqual(core.get_maintenance_mode(), True)
                self.assertEqual(core.get_maintenance_mode(), value)

    def test_context_manager_off(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for value in [True, False]:
                core.set_maintenance_mode(value)
                with core.maintenance_mode_off():
                    self.assertEqual(core.get_maintenance_mode(), False)
                self.assertEqual(core.get_maintenance_mode(), value)

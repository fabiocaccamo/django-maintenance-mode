import sys
from datetime import timedelta
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from maintenance_mode import core
from maintenance_mode.management.commands.maintenance_mode import (
    Command as MaintenanceModeCommand,
)

from .base import MaintenanceModeTestCase


class ManagementCommandsTestCase(MaintenanceModeTestCase):
    def test_management_commands(self):
        self._reset_state()

        call_command("maintenance_mode", "on")
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command("maintenance_mode", "off")
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_management_commands_invalid_file_path(self):
        self._reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        settings.MAINTENANCE_MODE_STATE_FILE_PATH = self.invalid_file_path

        with self.assertRaises((CommandError, OSError)):
            call_command("maintenance_mode", "on")

        with self.assertRaises((CommandError, OSError)):
            call_command("maintenance_mode", "off")

        with self.assertRaises((CommandError, OSError)):
            cmd = MaintenanceModeCommand()
            cmd.get_maintenance_mode()

        with self.assertRaises((CommandError, OSError)):
            cmd = MaintenanceModeCommand()
            cmd.set_maintenance_mode(True)

        settings.MAINTENANCE_MODE_STATE_FILE_PATH = file_path

    def test_management_commands_no_arguments(self):
        self._reset_state()

        with self.assertRaises(CommandError):
            call_command("maintenance_mode")

    def test_management_commands_invalid_argument(self):
        self._reset_state()

        with self.assertRaises(CommandError):
            call_command("maintenance_mode", "hello world")

    def test_management_commands_schedule(self):
        self._reset_state()

        one_hour = timedelta(hours=1)

        # active schedule
        call_command(
            "maintenance_mode", "on", end=(timezone.now() + one_hour).isoformat()
        )
        self.assertTrue(core.get_maintenance_mode())

        # schedule overwrites even if maintenance mode is already on
        call_command(
            "maintenance_mode", "on", start=(timezone.now() + one_hour).isoformat()
        )
        self.assertFalse(core.get_maintenance_mode())

        # invalid datetime value
        with self.assertRaises(CommandError):
            call_command("maintenance_mode", "on", end="not-a-datetime")

        # schedule options with 'off' state
        with self.assertRaises(CommandError):
            call_command(
                "maintenance_mode", "off", end=(timezone.now() + one_hour).isoformat()
            )

        # 'off' clears a stored schedule even if not active yet
        call_command(
            "maintenance_mode", "on", start=(timezone.now() + one_hour).isoformat()
        )
        call_command("maintenance_mode", "off")
        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        # plain 'on' overwrites a stored active schedule
        call_command(
            "maintenance_mode", "on", end=(timezone.now() + one_hour).isoformat()
        )
        call_command("maintenance_mode", "on")
        self.assertEqual(backend.get_value(), True)

    def test_management_commands_interactive(self):
        self._reset_state()

        sys_stdin = sys.stdin

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "on", interactive=True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "on", interactive=True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "off", interactive=True)
        val = core.get_maintenance_mode()
        self.assertFalse(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "off", interactive=True)
        val = core.get_maintenance_mode()
        self.assertFalse(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("n")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "on", interactive=True)
        val = core.get_maintenance_mode()
        self.assertFalse(val)
        confirm_answer_file.close()

        sys.stdin = sys_stdin

    def test_management_commands_verbose(self):
        self._reset_state()

        call_command("maintenance_mode", "on", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command("maintenance_mode", "on", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command("maintenance_mode", "off", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        call_command("maintenance_mode", "off", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        out = StringIO()
        call_command(
            "maintenance_mode",
            "on",
            end=(timezone.now() + timedelta(hours=1)).isoformat(),
            verbosity=3,
            stdout=out,
        )
        val = core.get_maintenance_mode()
        self.assertTrue(val)
        self.assertIn("scheduled", out.getvalue())

        call_command("maintenance_mode", "off", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

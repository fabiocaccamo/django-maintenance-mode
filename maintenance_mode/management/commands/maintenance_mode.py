from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from maintenance_mode import core


class Command(BaseCommand):
    args = "<on|off>"
    help = (
        f"run python manage.py maintenance_mode {args} to change maintenance-mode state"
    )

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("--start", dest="start", default=None)
        parser.add_argument("--end", dest="end", default=None)
        parser.add_argument("--interactive", dest="interactive", action="store_true")

    def get_maintenance_mode(self):
        try:
            value = core.get_maintenance_mode()
            return value
        except OSError as error:
            raise CommandError(
                "Unable to read state file at: "
                f"{settings.MAINTENANCE_MODE_STATE_FILE_NAME}"
            ) from error

    def set_maintenance_mode(self, value, start=None, end=None):
        try:
            core.set_maintenance_mode(value, start=start, end=end)
        except OSError as error:
            raise CommandError(
                "Unable to write state file at: "
                f"{settings.MAINTENANCE_MODE_STATE_FILE_NAME}"
            ) from error
        except (ImproperlyConfigured, TypeError, ValueError) as error:
            raise CommandError(str(error)) from error

    def set_maintenance_mode_with_confirm(
        self, value, confirm_message, interactive, start=None, end=None
    ):
        if interactive:
            if self.confirm(confirm_message):
                self.set_maintenance_mode(value, start=start, end=end)
        else:
            self.set_maintenance_mode(value, start=start, end=end)

    def confirm(self, message):
        input_func = input
        answer = input_func(message)
        answer = answer.lower()
        return answer.find("y") == 0

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        verbose = True if verbosity == 3 else False
        interactive = options.get("interactive", False)
        start = options.get("start")
        end = options.get("end")
        scheduled = start is not None or end is not None
        state = options["state"]
        state = state.lower()
        value = self.get_maintenance_mode()
        backend = core.get_maintenance_mode_backend()
        scheduled_state = isinstance(backend.get_value(), dict)

        if state in ["on", "yes", "true", "1"]:
            if value and not scheduled and not scheduled_state:
                if verbose:
                    self.stdout.write("maintenance mode is already on")
                return

            self.set_maintenance_mode_with_confirm(
                True, "maintenance mode on? (y/N) ", interactive, start=start, end=end
            )

        elif state in ["off", "no", "false", "0"]:
            if scheduled:
                raise CommandError(
                    "--start / --end options can only be used with 'on' state"
                )

            if not value and not scheduled_state:
                if verbose:
                    self.stdout.write("maintenance mode is already off")
                return

            self.set_maintenance_mode_with_confirm(
                False, "maintenance mode off? (y/N) ", interactive
            )

        else:
            raise CommandError(f"Invalid argument: {state!r} expected {self.args}")

        if verbose:
            state_str = "on" if self.get_maintenance_mode() else "off"
            raw_value = backend.get_value()
            if isinstance(raw_value, dict):
                state_str = f"{state_str} (scheduled: {raw_value})"
            output = f"maintenance mode: {state_str}"
            self.stdout.write(output)

        return

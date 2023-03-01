from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from maintenance_mode import core


class Command(BaseCommand):
    args = "<on|off>"
    help = (
        f"run python manage.py maintenance_mode {args} "
        "to change maintenance-mode state"
    )

    def add_arguments(self, parser):
        parser.add_argument("state")
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

    def set_maintenance_mode(self, value):
        try:
            core.set_maintenance_mode(value)
        except OSError as error:
            raise CommandError(
                "Unable to write state file at: "
                f"{settings.MAINTENANCE_MODE_STATE_FILE_NAME}"
            ) from error

    def set_maintenance_mode_with_confirm(self, value, confirm_message, interactive):
        if interactive:
            if self.confirm(confirm_message):
                self.set_maintenance_mode(value)
        else:
            self.set_maintenance_mode(value)

    def confirm(self, message):
        input_func = input
        answer = input_func(message)
        answer = answer.lower()
        return answer.find("y") == 0

    def handle(self, *args, **options):
        verbosity = int(options["verbosity"])
        verbose = True if verbosity == 3 else False
        interactive = options.get("interactive", False)
        state = options["state"]
        state = state.lower()
        value = self.get_maintenance_mode()

        if state in ["on", "yes", "true", "1"]:
            if value:
                if verbose:
                    self.stdout.write("maintenance mode is already on")
                return

            self.set_maintenance_mode_with_confirm(
                True, "maintenance mode on? (y/N) ", interactive
            )

        elif state in ["off", "no", "false", "0"]:
            if not value:
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
            output = f"maintenance mode: {state_str}"
            self.stdout.write(output)

        return

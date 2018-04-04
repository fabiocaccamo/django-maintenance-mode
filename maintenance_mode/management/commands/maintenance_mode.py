# -*- coding: utf-8 -*-

from __future__ import absolute_import

import django

from django.core.management.base import BaseCommand, CommandError

from maintenance_mode import core


class Command(BaseCommand):

    args = '<on|off>'
    help = 'run python manage.py maintenance_mode %s '\
           'to change maintenance-mode state' % args

    def add_arguments(self, parser):
        parser.add_argument('state')

    def confirm(self, message):
        # Fix for Python 2.x.
        try:
            input_func = raw_input
        except NameError:
            input_func = input

        answer = input_func(message)
        answer = answer.lower()
        return answer.find('y') == 0

    def set_mode(self, mode):
        """Set the maintenance mode.

        Wrapper to catch IO errors.
        """
        try:
            core.set_maintenance_mode(mode)
        except IOError:
            raise CommandError("Can't set maintenance mode (unable to write lock file).")

    def handle(self, *args, **options):

        verbosity = int(options['verbosity'])
        verbose = True if verbosity == 3 else False

        if django.VERSION < (1, 8):
            if len(args) != 1:
                raise CommandError(
                    'Error: expected 1 argument: %s' % (self.args, ))

            state = args[0]
        else:
            state = options['state']

        state = state.lower()
        try:
            value = core.get_maintenance_mode()
        except IOError:
            raise CommandError("Can't get maintenance mode (unable to open lock file).")

        if state in ['on', 'yes', 'true', '1']:

            if value:
                if verbose:
                    self.stdout.write('maintenance mode is already on')
                return

            if verbose:
                if self.confirm('maintenance mode on? (y/N) '):
                    self.set_mode(True)
            else:
                self.set_mode(True)

        elif state in ['off', 'no', 'false', '0']:

            if not value:
                if verbose:
                    self.stdout.write('maintenance mode is already off')
                return

            if verbose:
                if self.confirm('maintenance mode off? (y/N) '):
                    self.set_mode(False)
            else:
                self.set_mode(False)

        else:
            raise CommandError('Error: invalid argument: \'%s\' '
                               'expected %s' % (state, self.args, ))

        if verbose:
            output = 'maintenance mode: %s' % (
                'on' if core.get_maintenance_mode() else 'off', )
            self.stdout.write(output)

        return

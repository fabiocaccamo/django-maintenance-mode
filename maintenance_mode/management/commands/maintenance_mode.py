# -*- coding: utf-8 -*-

from __future__ import absolute_import

import django

from django.core.management.base import BaseCommand, CommandError

from maintenance_mode import core


class Command(BaseCommand):

    args = '<on|off>'
    help = 'run python manage.py maintenance_mode %s to change maintenance-mode state' % args

    def add_arguments(self, parser):

        parser.add_argument('state')

    def handle(self, *args, **options):

        if django.VERSION < (1, 8):

            if len(args) != 1:
                raise CommandError('Error: expected 1 argument: %s' % (self.args, ))

            state = args[0]
        else:
            state = options['state']

        state = state.lower()

        if state in ['on', 'yes', 'true', '1']:
            core.set_maintenance_mode(True)

        elif state in ['off', 'no', 'false', '0']:
            core.set_maintenance_mode(False)
        else:
            raise CommandError('Error: invalid argument: \'%s\' expected %s' % (state, self.args, ))


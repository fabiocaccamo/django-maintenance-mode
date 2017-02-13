# -*- coding: utf-8 -*-

from __future__ import absolute_import

import django
from django.core.management.base import BaseCommand

from maintenance_mode import core, __version__


class Command(BaseCommand):
    
    args = '<on|off>'
    help = 'run python manage.py maintenance_mode %s to change maintenance-mode state' % args
    missing_args_message = "Specify one of %s" % args
    
    def get_version(self):
        return __version__

    def add_arguments(self, parser):
            parser.add_argument(
                'flag',
                help=self.args
            )

    def handle(self, *args, **options):

        flag = options["flag"]
        
        if flag:
            
            arg_value = flag.lower()
            
            if arg_value in ['on', 'yes', 'true', '1']:
                core.set_maintenance_mode(True)
                return
                
            elif arg_value in ['off', 'no', 'false', '0']:
                core.set_maintenance_mode(False)
                return
                
        print(self.help)
        
        

# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.management.base import BaseCommand

from maintenance_mode import core


class Command(BaseCommand):
    
    args = '<on|off>'
    help = 'run python manage.py maintenance_mode %s to change maintenance-mode state' % args
    
    def handle(self, *args, **options):
        
        if len(args) > 0:
            
            arg_value = args[0].lower()
            
            if arg_value in ['on', 'yes', 'true', '1']:
                core.set_maintenance_mode(True)
                return
                
            elif arg_value in ['off', 'no', 'false', '0']:
                core.set_maintenance_mode(False)
                return
                
        print(self.help)
        
        
# django-maintenance-mode
django-maintenance-mode shows a 503 error page when maintenance-mode is on.

##Installation

1. Run ``pip install django-maintenance-mode`` or [download django-maintenance-mode](http://pypi.python.org/pypi/django-maintenance-mode) and add the **maintenance_mode** package to your project
2. Add ``'maintenance_mode'`` to ``settings.INSTALLED_APPS`` before custom applications
3. Add ``'maintenance_mode.middleware.MaintenanceModeMiddleware'`` to ``settings.MIDDLEWARE_CLASSES`` as last middleware
4. Add your custom ``templates/503.html`` file
5. Restart your application server

##Configuration (optional)

All these settings are optional, if not defined in ``settings.py`` the default values (listed below) will be used.

```python

#if True the maintenance-mode will be activated
MAINTENANCE_MODE = False

#if True the staff will not see the maintenance-mode page
MAINTENANCE_MODE_EXCLUDE_STAFF = False

#if True the superuser will not see the maintenance-mode page
MAINTENANCE_MODE_EXCLUDE_SUPERUSER = False

#list of urls that will not be affected by the maintenance-mode page
#urls will be used to compile regular expressions objects
MAINTENANCE_MODE_IGNORE_URLS = ()

#the template that will be shown by the maintenance-mode page
MAINTENANCE_MODE_TEMPLATE = '503.html'

#the timeout (in seconds) after which the maintenance-mode will be automatically deactivated
#use it at your own risk
MAINTENANCE_MODE_TIMEOUT = None
```

##Usage

####Python

```python
# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        call_command('maintenance_mode', 'on')
        
        #call your command(s)
        
        call_command('maintenance_mode', 'off')
        
        
        
```

####Commands

Run ``python manage.py maintenance_mode <on|off>``

[![Build Status](https://travis-ci.org/fabiocaccamo/django-maintenance-mode.svg?branch=master)](https://travis-ci.org/fabiocaccamo/django-maintenance-mode)
[![Financial Contributors on Open Collective](https://opencollective.com/django-maintenance-mode/all/badge.svg?label=financial+contributors)](https://opencollective.com/django-maintenance-mode) [![coverage](https://codecov.io/gh/fabiocaccamo/django-maintenance-mode/branch/master/graph/badge.svg)](https://codecov.io/gh/fabiocaccamo/django-maintenance-mode)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/918668ac85e74206a4d8d95923548d79)](https://www.codacy.com/app/fabiocaccamo/django-maintenance-mode)
[![Requirements Status](https://requires.io/github/fabiocaccamo/django-maintenance-mode/requirements.svg?branch=master)](https://requires.io/github/fabiocaccamo/django-maintenance-mode/requirements/?branch=master)
[![PyPI version](https://badge.fury.io/py/django-maintenance-mode.svg)](https://badge.fury.io/py/django-maintenance-mode)
[![PyPI downloads](https://img.shields.io/pypi/dm/django-maintenance-mode.svg)](https://img.shields.io/pypi/dm/django-maintenance-mode.svg)
[![Py versions](https://img.shields.io/pypi/pyversions/django-maintenance-mode.svg)](https://img.shields.io/pypi/pyversions/django-maintenance-mode.svg)
[![License](https://img.shields.io/pypi/l/django-maintenance-mode.svg)](https://img.shields.io/pypi/l/django-maintenance-mode.svg)

# django-maintenance-mode
django-maintenance-mode shows a 503 error page when **maintenance-mode** is **on**.

It works at application level, so your django instance should be up.

It doesn't use database and doesn't prevent database access.

## Requirements
- Python 2.7, 3.4, 3.5, 3.6, 3.7
- Django 1.7, 1.8, 1.9, 1.10, 1.11, 2.0, 2.1, 2.2

## Installation

1. Run ``pip install django-maintenance-mode`` or [download django-maintenance-mode](http://pypi.python.org/pypi/django-maintenance-mode) and add the **maintenance_mode** package to your project
2. Add ``'maintenance_mode'`` to ``settings.INSTALLED_APPS`` before custom applications
3. Add ``'maintenance_mode.middleware.MaintenanceModeMiddleware'`` to ``settings.MIDDLEWARE_CLASSES``/``settings.MIDDLEWARE`` as last middleware
4. Add ``'maintenance_mode.context_processors.maintenance_mode'`` to ``settings.CONTEXT_PROCESSORS``
5. Add your custom ``templates/503.html`` file
6. Restart your application server

## Configuration (optional)

#### Settings
All these settings are optional, if not defined in ``settings.py`` the default values (listed below) will be used.

```python
# if True the maintenance-mode will be activated
MAINTENANCE_MODE = None
```

```python
# by default, to get/set the state value a local file backend is used
# if you want to use the db or cache, you can create a custom backend
# custom backends must extend 'maintenance_mode.backends.AbstractStateBackend' class
# and implement get_value(self) and set_value(self, val) methods
MAINTENANCE_MODE_STATE_BACKEND = 'maintenance_mode.backends.LocalFileBackend'
```

```python
# by default, a file named "maintenance_mode_state.txt" will be created in the maintenance_mode directory
# you can customize the state file path in case the default one is not writable
MAINTENANCE_MODE_STATE_FILE_PATH = 'maintenance_mode_state.txt'
```

```python
# if True admin site will not be affected by the maintenance-mode page
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
```

```python
# if True anonymous users will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
```

```python
# if True authenticated users will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = False
```

```python
# if True the staff will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_STAFF = False
```

```python
# if True the superuser will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_SUPERUSER = False
```

```python
# list of ip-addresses that will not be affected by the maintenance-mode
# ip-addresses will be used to compile regular expressions objects
MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = ()
```

```python
# the path of the function that will return the client IP address given the request object -> 'myapp.mymodule.myfunction'
# the default function ('maintenance_mode.utils.get_client_ip_address') returns request.META['REMOTE_ADDR']
# in some cases the default function returns None, to avoid this scenario just use 'django-ipware'
MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = None
```
Retrieve user's real IP address using [`django-ipware`](https://github.com/un33k/django-ipware):
```python
MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = 'ipware.ip.get_ip'
```

```python
# list of urls that will not be affected by the maintenance-mode
# urls will be used to compile regular expressions objects
MAINTENANCE_MODE_IGNORE_URLS = ()
```

```python
# if True the maintenance mode will not return 503 response while running tests
# useful for running tests while maintenance mode is on, before opening the site to public use
MAINTENANCE_MODE_IGNORE_TESTS = False
```

```python
# the absolute url where users will be redirected to during maintenance-mode
MAINTENANCE_MODE_REDIRECT_URL = None
```

```python
# the template that will be shown by the maintenance-mode page
MAINTENANCE_MODE_TEMPLATE = '503.html'
```

```python
# the path of the function that will return the template context -> 'myapp.mymodule.myfunction'
MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT = None
```

```python
# the HTTP status code to send
MAINTENANCE_MODE_STATUS_CODE = 503
```

```python
# the value in seconds of the Retry-After header during maintenance-mode
MAINTENANCE_MODE_RETRY_AFTER = 3600 # 1 hour
```

#### URLs
Add **maintenance_mode.urls** to ``urls.py`` if you want superusers able to set maintenance_mode using urls.

```python
urlpatterns = [
    # ...
    url(r'^maintenance-mode/', include('maintenance_mode.urls')),
    # ...
]
```

#### Context Processors
Add **maintenance_mode.context_processors.maintenance_mode** to your context_processors list in ``settings.py`` if you want to access the maintenance_mode status in your templates.

```python
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ...
                'maintenance_mode.context_processors.maintenance_mode',
                # ...
            ],
        },
        # ...
    },
]
```

#### Views
You can force maintenance mode on/off at view level using view decorators:

```python
from maintenance_mode.decorators import force_maintenance_mode_off, force_maintenance_mode_on

@force_maintenance_mode_off
def my_view_a(request):
    # never return 503 response
    pass

@force_maintenance_mode_on
def my_view_b(request):
    # always return 503 response
    pass
```

## Usage

#### Python
```python
from maintenance_mode.core import get_maintenance_mode, set_maintenance_mode

set_maintenance_mode(True)

if get_maintenance_mode():
    set_maintenance_mode(False)
```
or
```python
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        call_command('maintenance_mode', 'on')

        # call your command(s)

        call_command('maintenance_mode', 'off')



```

#### Templates
```html
{% if maintenance_mode %}
<!-- html -->
{% endif %}
```

#### Terminal

Run ``python manage.py maintenance_mode <on|off>``

*(**This is not Heroku-friendly because** any execution of heroku run* `manage.py` *will be run on a separate worker dyno, not the web one. Therefore **the state-file is set but on the wrong machine**)*

#### URLs
Superusers can change maintenance-mode using the following urls:

``/maintenance-mode/off/``

``/maintenance-mode/on/``

## Contributors

### Code Contributors

This project exists thanks to all the people who contribute. [[Contribute](CONTRIBUTING.md)].
<a href="https://github.com/fabiocaccamo/django-maintenance-mode/graphs/contributors"><img src="https://opencollective.com/django-maintenance-mode/contributors.svg?width=890&button=false" /></a>

### Financial Contributors

Become a financial contributor and help us sustain our community. [[Contribute](https://opencollective.com/django-maintenance-mode/contribute)]

#### Individuals

<a href="https://opencollective.com/django-maintenance-mode"><img src="https://opencollective.com/django-maintenance-mode/individuals.svg?width=890"></a>

#### Organizations

Support this project with your organization. Your logo will show up here with a link to your website. [[Contribute](https://opencollective.com/django-maintenance-mode/contribute)]

<a href="https://opencollective.com/django-maintenance-mode/organization/0/website"><img src="https://opencollective.com/django-maintenance-mode/organization/0/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/1/website"><img src="https://opencollective.com/django-maintenance-mode/organization/1/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/2/website"><img src="https://opencollective.com/django-maintenance-mode/organization/2/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/3/website"><img src="https://opencollective.com/django-maintenance-mode/organization/3/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/4/website"><img src="https://opencollective.com/django-maintenance-mode/organization/4/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/5/website"><img src="https://opencollective.com/django-maintenance-mode/organization/5/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/6/website"><img src="https://opencollective.com/django-maintenance-mode/organization/6/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/7/website"><img src="https://opencollective.com/django-maintenance-mode/organization/7/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/8/website"><img src="https://opencollective.com/django-maintenance-mode/organization/8/avatar.svg"></a>
<a href="https://opencollective.com/django-maintenance-mode/organization/9/website"><img src="https://opencollective.com/django-maintenance-mode/organization/9/avatar.svg"></a>

## License
Released under [MIT License](LICENSE.txt).

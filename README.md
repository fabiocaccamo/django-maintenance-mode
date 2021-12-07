[![](https://img.shields.io/pypi/pyversions/django-maintenance-mode.svg?color=3776AB&logo=python&logoColor=white)](https://www.python.org/)
[![](https://img.shields.io/pypi/djversions/django-maintenance-mode?color=0C4B33&logo=django&logoColor=white&label=django)](https://www.djangoproject.com/)

[![](https://img.shields.io/pypi/v/django-maintenance-mode.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-maintenance-mode/)
[![](https://pepy.tech/badge/django-maintenance-mode)](https://pepy.tech/project/django-maintenance-mode)
[![](https://img.shields.io/github/stars/fabiocaccamo/django-maintenance-mode?logo=github)](https://github.com/fabiocaccamo/django-maintenance-mode/)
[![](https://badges.pufler.dev/visits/fabiocaccamo/django-maintenance-mode?label=visitors&color=blue)](https://badges.pufler.dev)
[![](https://img.shields.io/pypi/l/django-maintenance-mode.svg?color=blue)](https://github.com/fabiocaccamo/django-maintenance-mode/blob/master/LICENSE.txt)

[![](https://img.shields.io/github/workflow/status/fabiocaccamo/django-maintenance-mode/Python%20package?label=build&logo=github)](https://github.com/fabiocaccamo/django-maintenance-mode)
[![](https://img.shields.io/codecov/c/gh/fabiocaccamo/django-maintenance-mode?logo=codecov)](https://codecov.io/gh/fabiocaccamo/django-maintenance-mode)
[![](https://img.shields.io/codacy/grade/918668ac85e74206a4d8d95923548d79?logo=codacy)](https://www.codacy.com/app/fabiocaccamo/django-maintenance-mode)
[![](https://img.shields.io/codeclimate/maintainability/fabiocaccamo/django-maintenance-mode?logo=code-climate)](https://codeclimate.com/github/fabiocaccamo/django-maintenance-mode/)
[![](https://requires.io/github/fabiocaccamo/django-maintenance-mode/requirements.svg?branch=master)](https://requires.io/github/fabiocaccamo/django-maintenance-mode/requirements/?branch=master)

# django-maintenance-mode
django-maintenance-mode shows a 503 error page when **maintenance-mode** is **on**.

It works at application level, so your django instance should be up.

It doesn't use database and doesn't prevent database access.

## Installation

1. Run ``pip install django-maintenance-mode`` or [download django-maintenance-mode](http://pypi.python.org/pypi/django-maintenance-mode) and add the **maintenance_mode** package to your project
2. Add ``'maintenance_mode'`` to ``settings.INSTALLED_APPS`` before custom applications
3. Add ``'maintenance_mode.middleware.MaintenanceModeMiddleware'`` to ``settings.MIDDLEWARE_CLASSES``/``settings.MIDDLEWARE`` as last middleware
4. Add your custom ``templates/503.html`` file
5. Restart your application server

## Configuration (optional)

### Settings
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

# alternatively it is possible to use the default storage backend
MAINTENANCE_MODE_STATE_BACKEND = 'maintenance_mode.backends.DefaultStorageBackend'
```

```python
# by default, a file named "maintenance_mode_state.txt" will be created in the settings.py directory
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

#### Logging
You can disable emailing 503 errors to admins while maintenance mode is enabled:

```python
LOGGING = {
    'filters': {
        'require_not_maintenance_mode_503': {
            '()': 'maintenance_mode.logging.RequireNotMaintenanceMode503',
        },
        ...
    },
    'handlers': {
        ...
    },
    ...
}
```

### Context Managers
You can force a block of code execution to run under maintenance mode or not using context managers:

```python
from maintenance_mode.core import maintenance_mode_off, maintenance_mode_on

with maintenance_mode_on():
    # do stuff
    pass

with maintenance_mode_off():
    # do stuff
    pass
```

### URLs
Add **maintenance_mode.urls** to ``urls.py`` if you want superusers able to set maintenance_mode using urls.

```python
urlpatterns = [
    # ...
    url(r'^maintenance-mode/', include('maintenance_mode.urls')),
    # ...
]
```

### Views
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

### Python
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

### Templates
```html
{% if maintenance_mode %}
<!-- html -->
{% endif %}
```

### Terminal

Run ``python manage.py maintenance_mode <on|off>``

*(**This is not Heroku-friendly because** any execution of heroku run* `manage.py` *will be run on a separate worker dyno, not the web one. Therefore **the state-file is set but on the wrong machine. You should use a custom*** `MAINTENANCE_MODE_STATE_BACKEND`*.)*

### URLs
Superusers can change maintenance-mode using the following urls:

``/maintenance-mode/off/``

``/maintenance-mode/on/``

## Testing
```bash
# create python virtual environment
virtualenv testing_django_maintenance_mode

# activate virtualenv
cd testing_django_maintenance_mode && . bin/activate

# clone repo
git clone https://github.com/fabiocaccamo/django-maintenance-mode.git src && cd src

# install requirements
pip install -r requirements.txt
pip install -r requirements-test.txt

# run tests
tox
# or
python setup.py test
# or
python -m django test --settings "tests.settings"
```

## License
Released under [MIT License](LICENSE.txt).

---

## See also

- [`django-admin-interface`](https://github.com/fabiocaccamo/django-admin-interface) - the default admin interface made customizable by the admin itself. popup windows replaced by modals. 🧙 ⚡

- [`django-colorfield`](https://github.com/fabiocaccamo/django-colorfield) - simple color field for models with a nice color-picker in the admin. 🎨

- [`django-extra-settings`](https://github.com/fabiocaccamo/django-extra-settings) - config and manage typed extra settings using just the django admin. ⚙️

- [`django-redirects`](https://github.com/fabiocaccamo/django-redirects) - redirects with full control. ↪️

- [`django-treenode`](https://github.com/fabiocaccamo/django-treenode) - probably the best abstract model / admin for your tree based stuff. 🌳

- [`python-benedict`](https://github.com/fabiocaccamo/python-benedict) - dict subclass with keylist/keypath support, I/O shortcuts (base64, csv, json, pickle, plist, query-string, toml, xml, yaml) and many utilities. 📘

- [`python-codicefiscale`](https://github.com/fabiocaccamo/python-codicefiscale) - encode/decode Italian fiscal codes - codifica/decodifica del Codice Fiscale. 🇮🇹 💳

- [`python-fontbro`](https://github.com/fabiocaccamo/python-fontbro) - friendly font operations. 🧢

- [`python-fsutil`](https://github.com/fabiocaccamo/python-fsutil) - file-system utilities for lazy devs. 🧟‍♂️

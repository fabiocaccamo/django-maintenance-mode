|Build Status| |coverage| |Code Health| |Requirements Status| |PyPI version| |Py versions| |License|

django-maintenance-mode
=======================

django-maintenance-mode shows a 503 error page when **maintenance-mode** is **on**.

It works at application level, so your django instance should be up.

It doesn't use database and doesn't prevent database access.

Requirements
------------

-  Python 2.7, 3.4, 3.5, 3.6
-  Django 1.7, 1.8, 1.9, 1.10, 1.11, 2.0

Installation
------------

1. Run ``pip install django-maintenance-mode`` or `download
   django-maintenance-mode <http://pypi.python.org/pypi/django-maintenance-mode>`__
   and add the **maintenance_mode** package to your project
2. Add ``'maintenance_mode'`` to ``settings.INSTALLED_APPS`` before
   custom applications
3. Add ``'maintenance_mode.middleware.MaintenanceModeMiddleware'`` to
   ``settings.MIDDLEWARE_CLASSES``/``settings.MIDDLEWARE`` as last middleware
4. Add your custom ``templates/503.html`` file
5. Restart your application server

Configuration (optional)
------------------------

All these settings are optional, if not defined in ``settings.py`` the
default values (listed below) will be used.

.. code:: python

    # if True the maintenance-mode will be activated
    MAINTENANCE_MODE = None

.. code:: python

    # by default, a file named "maintenance_mode_state.txt" will be created in the maintenance_mode directory
    # you can customize the state file path in case the default one is not writable
    MAINTENANCE_MODE_STATE_FILE_PATH = 'maintenance_mode_state.txt'

.. code:: python

    # if True the staff will not see the maintenance-mode page
    MAINTENANCE_MODE_IGNORE_STAFF = False

.. code:: python

    # if True the superuser will not see the maintenance-mode page
    MAINTENANCE_MODE_IGNORE_SUPERUSER = False

.. code:: python

    # list of ip-addresses that will not be affected by the maintenance-mode
    # ip-addresses will be used to compile regular expressions objects
    MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = ()

.. code:: python

    # the path of the function that will return the client IP address given the request object -> 'myapp.mymodule.myfunction'
    # the default function ('maintenance_mode.utils.get_client_ip_address') returns request.META['REMOTE_ADDR']
    MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = None

Retrieve user's real IP address using
`django-ipware <https://github.com/un33k/django-ipware>`__:

.. code:: python

    MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = 'ipware.ip.get_ip'

.. code:: python

    # list of urls that will not be affected by the maintenance-mode
    # urls will be used to compile regular expressions objects
    MAINTENANCE_MODE_IGNORE_URLS = ()

.. code:: python

    # if True the maintenance mode will not return 503 response while running tests
    # useful for running tests while maintenance mode is on, before opening the site to public use
    MAINTENANCE_MODE_IGNORE_TESTS = False

.. code:: python

    # the absolute url where users will be redirected to during maintenance-mode
    MAINTENANCE_MODE_REDIRECT_URL = None

.. code:: python

    # the template that will be shown by the maintenance-mode page
    MAINTENANCE_MODE_TEMPLATE = '503.html'

.. code:: python

    # the path of the function that will return the template context -> 'myapp.mymodule.myfunction'
    MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT = None

Add **maintenance\_mode.urls** to ``urls.py`` if you want superusers
able to set maintenance\_mode using urls.

.. code:: python

    urlpatterns = [
        # ...
        url(r'^maintenance-mode/', include('maintenance_mode.urls')),
        # ...
    ]

Add **maintenance\_mode.context\_processors.maintenance\_mode** to your
context\_processors list in ``settings.py`` if you want to access the
maintenance\_mode status in your templates.

.. code:: python

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

Usage
-----

Python
~~~~~~

.. code:: python

    from maintenance_mode.core import get_maintenance_mode, set_maintenance_mode

    set_maintenance_mode(True)

    if get_maintenance_mode():
        set_maintenance_mode(False)

or

.. code:: python

    from django.core.management import call_command
    from django.core.management.base import BaseCommand


    class Command(BaseCommand):

        def handle(self, *args, **options):

            call_command('maintenance_mode', 'on')

            # call your command(s)

            call_command('maintenance_mode', 'off')


Templates
~~~~~~~~~

.. code:: html

    {% if maintenance_mode %}
    <!-- html -->
    {% endif %}

Terminal
~~~~~~~~

Run ``python manage.py maintenance_mode <on|off>``

*(This is not Heroku-friendly because any execution of heroku run*
``manage.py`` *will be run on a separate worker dyno, not the web one.
Therefore the state-file is set but on the wrong machine)*

URLs
~~~~

Superusers can change maintenance-mode using the following urls:

``/maintenance-mode/off/``

``/maintenance-mode/on/``

License
-------

Released under `MIT License <LICENSE>`__.

.. |Build Status| image:: https://travis-ci.org/fabiocaccamo/django-maintenance-mode.svg?branch=master
.. |coverage| image:: https://codecov.io/gh/fabiocaccamo/django-maintenance-mode/branch/master/graph/badge.svg
.. |Code Health| image:: https://landscape.io/github/fabiocaccamo/django-maintenance-mode/master/landscape.svg?style=flat
.. |Requirements Status| image:: https://requires.io/github/fabiocaccamo/django-maintenance-mode/requirements.svg?branch=master
.. |PyPI version| image:: https://badge.fury.io/py/django-maintenance-mode.svg
.. |Py versions| image:: https://img.shields.io/pypi/pyversions/django-maintenance-mode.svg
.. |License| image:: https://img.shields.io/pypi/l/django-maintenance-mode.svg

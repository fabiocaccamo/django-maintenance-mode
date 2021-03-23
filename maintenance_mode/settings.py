# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.module_loading import import_module

import os


if not hasattr(settings, 'MAINTENANCE_MODE'):
    settings.MAINTENANCE_MODE = None

if not hasattr(settings, 'MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS'):
    settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = None

if not hasattr(settings, 'MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT'):
    settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT = None

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_ADMIN_SITE'):
    settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = None

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER'):
    settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER'):
    settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = False

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_IP_ADDRESSES'):
    settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_STAFF'):
    settings.MAINTENANCE_MODE_IGNORE_STAFF = False

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_SUPERUSER'):
    settings.MAINTENANCE_MODE_IGNORE_SUPERUSER = False

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_TESTS'):
    settings.MAINTENANCE_MODE_IGNORE_TESTS = False

if not hasattr(settings, 'MAINTENANCE_MODE_IGNORE_URLS'):
    settings.MAINTENANCE_MODE_IGNORE_URLS = None

if not hasattr(settings, 'MAINTENANCE_MODE_REDIRECT_URL'):
    settings.MAINTENANCE_MODE_REDIRECT_URL = None

if not hasattr(settings, 'MAINTENANCE_MODE_STATE_BACKEND'):
    settings.MAINTENANCE_MODE_STATE_BACKEND = 'maintenance_mode.backends.LocalFileBackend'

if not hasattr(settings, 'MAINTENANCE_MODE_STATE_FILE_NAME'):
    settings.MAINTENANCE_MODE_STATE_FILE_NAME = 'maintenance_mode_state.txt'

if not hasattr(settings, 'MAINTENANCE_MODE_STATE_FILE_PATH'):
    settings_module = import_module(os.environ['DJANGO_SETTINGS_MODULE'])
    settings_path = settings_module.__file__
    settings_dir = os.path.dirname(settings_path)
    settings.MAINTENANCE_MODE_STATE_FILE_PATH = os.path.abspath(
        os.path.join(settings_dir,
            settings.MAINTENANCE_MODE_STATE_FILE_NAME))

if not hasattr(settings, 'MAINTENANCE_MODE_TEMPLATE'):
    settings.MAINTENANCE_MODE_TEMPLATE = '503.html'

if not hasattr(settings, 'MAINTENANCE_MODE_STATUS_CODE'):
    settings.MAINTENANCE_MODE_STATUS_CODE = 503

if not hasattr(settings, 'MAINTENANCE_MODE_RETRY_AFTER'):
    settings.MAINTENANCE_MODE_RETRY_AFTER = 3600

# -*- coding: utf-8 -*-

from django.conf import settings

import os

if not hasattr(settings, 'MAINTENANCE_MODE'):
    settings.MAINTENANCE_MODE = None
if not hasattr(settings, 'MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS'):
    settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = None
if not hasattr(settings, 'MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT'):
    settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT = None
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
if not hasattr(settings, 'MAINTENANCE_MODE_STATE_FILE_PATH'):
    settings.MAINTENANCE_MODE_STATE_FILE_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'maintenance_mode_state.txt')
if not hasattr(settings, 'MAINTENANCE_MODE_TEMPLATE'):
    settings.MAINTENANCE_MODE_TEMPLATE = '503.html'

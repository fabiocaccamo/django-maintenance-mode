# -*- coding: utf-8 -*-

from django.conf import settings

import os
import re


MAINTENANCE_MODE = getattr(settings, 'MAINTENANCE_MODE', False)
MAINTENANCE_MODE_STATE_FILE_PATH = getattr(settings, 'MAINTENANCE_MODE_STATE_FILE_PATH', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'maintenance_mode_state.txt'))

MAINTENANCE_MODE_IGNORE_STAFF = getattr(settings, 'MAINTENANCE_MODE_IGNORE_STAFF', False)
MAINTENANCE_MODE_IGNORE_SUPERUSER = getattr(settings, 'MAINTENANCE_MODE_IGNORE_SUPERUSER', False)

MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = getattr(settings, 'MAINTENANCE_MODE_IGNORE_IP_ADDRESSES', ())
MAINTENANCE_MODE_IGNORE_IP_ADDRESSES_RE = tuple([re.compile(ip_address) for ip_address in MAINTENANCE_MODE_IGNORE_IP_ADDRESSES])

MAINTENANCE_MODE_IGNORE_URLS = getattr(settings, 'MAINTENANCE_MODE_IGNORE_URLS', ())
MAINTENANCE_MODE_IGNORE_URLS_RE = tuple([re.compile(url) for url in MAINTENANCE_MODE_IGNORE_URLS])

MAINTENANCE_MODE_REDIRECT_URL = getattr(settings, 'MAINTENANCE_MODE_REDIRECT_URL', None)

if MAINTENANCE_MODE_REDIRECT_URL and MAINTENANCE_MODE_REDIRECT_URL[0:4].lower() != 'http':
    raise ValueError('MAINTENANCE_MODE_REDIRECT_URL should be an absolute url: %s' % MAINTENANCE_MODE_REDIRECT_URL)

MAINTENANCE_MODE_TEMPLATE = getattr(settings, 'MAINTENANCE_MODE_TEMPLATE', '503.html')
MAINTENANCE_MODE_TEMPLATE_CONTEXT = getattr(settings, 'MAINTENANCE_MODE_TEMPLATE_CONTEXT', None)


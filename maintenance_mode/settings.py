# -*- coding: utf-8 -*-

from django.conf import settings

import os
import re


MAINTENANCE_MODE = getattr(settings, 'MAINTENANCE_MODE', False)
MAINTENANCE_MODE_EXCLUDE_STAFF = getattr(settings, 'MAINTENANCE_MODE_EXCLUDE_STAFF', False)
MAINTENANCE_MODE_EXCLUDE_SUPERUSER = getattr(settings, 'MAINTENANCE_MODE_EXCLUDE_SUPERUSER', False)
MAINTENANCE_MODE_STATE_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'maintenance_mode_state.txt')

MAINTENANCE_MODE_IGNORE_URLS = getattr(settings, 'MAINTENANCE_MODE_IGNORE_URLS', ())
MAINTENANCE_MODE_IGNORE_URLS_RE = tuple([re.compile(url) for url in MAINTENANCE_MODE_IGNORE_URLS])
MAINTENANCE_MODE_TEMPLATE = getattr(settings, 'MAINTENANCE_MODE_TEMPLATE', '503.html')


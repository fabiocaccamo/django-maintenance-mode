# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf import settings

import logging


class RequireNotMaintenanceMode503(logging.Filter):
    """
    Filters out 503 errors if maintenance mode is activated.
    """

    def filter(self, record):
        """
        Return False if maintenance mode is on and
        the given record has a status code of 503.
        """
        status_code = getattr(record, 'status_code', None)
        if settings.MAINTENANCE_MODE and status_code == 503:
            return False
        return True

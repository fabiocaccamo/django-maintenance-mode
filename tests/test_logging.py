from django.conf import settings

from maintenance_mode.logging import RequireNotMaintenanceMode503

from .base import MaintenanceModeTestCase


class LoggingTestCase(MaintenanceModeTestCase):
    def test_logging_filter(self):
        self._reset_state()

        class Record:
            status_code = 0

        f = RequireNotMaintenanceMode503()
        r = Record()

        settings.MAINTENANCE_MODE = True
        r.status_code = 503
        self.assertFalse(f.filter(r))
        r.status_code = 200
        self.assertTrue(f.filter(r))

        settings.MAINTENANCE_MODE = False
        r.status_code = 503
        self.assertTrue(f.filter(r))
        r.status_code = 200
        self.assertTrue(f.filter(r))

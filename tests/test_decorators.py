from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from .base import MaintenanceModeTestCase
from .views import force_maintenance_mode_off_view, force_maintenance_mode_on_view


class DecoratorsTestCase(MaintenanceModeTestCase):
    def test_decorators_with_middleware(self):
        self._reset_state()

        url = reverse("maintenance_mode_off_view_func")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertOkResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertOkResponse(response)

        url = reverse("maintenance_mode_off_view_class")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertOkResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertOkResponse(response)

        url = reverse("maintenance_mode_on_view_func")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

        url = reverse("maintenance_mode_on_view_class")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            # 'maintenance_mode.middleware.MaintenanceModeMiddleware',
        ]
    )
    def test_decorators_without_middleware(self):
        self._reset_state()

        url = reverse("maintenance_mode_off_view_func")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertOkResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertOkResponse(response)

        url = reverse("maintenance_mode_off_view_class")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertOkResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertOkResponse(response)

        url = reverse("maintenance_mode_on_view_func")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

        url = reverse("maintenance_mode_on_view_class")

        settings.MAINTENANCE_MODE = True
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.client.get(url)
        self.assertMaintenanceResponse(response)

    def test_decorators_attrs(self):
        self.assertEqual(
            force_maintenance_mode_off_view.__name__, "force_maintenance_mode_off_view"
        )
        self.assertEqual(
            force_maintenance_mode_on_view.__name__, "force_maintenance_mode_on_view"
        )

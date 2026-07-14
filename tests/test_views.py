from django.urls import reverse

from maintenance_mode import core, views

from .base import MaintenanceModeTestCase


class ViewsTestCase(MaintenanceModeTestCase):
    def test_urls(self):
        self._reset_state()

        url = reverse("maintenance_mode_on")
        response = self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertRedirects(response, "/")
        self.assertFalse(val)

        url = reverse("maintenance_mode_off")
        response = self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertRedirects(response, "/")
        self.assertFalse(val)

    def test_urls_superuser(self):
        self._reset_state()

        self._login_superuser()

        url = reverse("maintenance_mode_on")
        self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        url = reverse("maintenance_mode_off")
        self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        self._logout()

    def test_context_processor(self):
        self._reset_state()

        core.set_maintenance_mode(True)
        response = self.client.get("/")
        val = response.context.get("maintenance_mode", False)
        self.assertTrue(val)
        core.set_maintenance_mode(False)

    def test_views(self):
        self._reset_state()

        url = reverse("maintenance_mode_on")
        request = self._get_anonymous_user_request(url)
        views.maintenance_mode_on(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        url = reverse("maintenance_mode_off")
        request = self._get_anonymous_user_request(url)
        views.maintenance_mode_off(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_views_superuser(self):
        self._reset_state()

        url = reverse("maintenance_mode_on")
        request = self._get_superuser_request(url)
        views.maintenance_mode_on(request)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        url = reverse("maintenance_mode_off")
        request = self._get_superuser_request(url)
        views.maintenance_mode_off(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

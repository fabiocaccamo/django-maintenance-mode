from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase

from maintenance_mode import http


class TestGetMaintenanceResponse(SimpleTestCase):
    """Test `http.get_maintenance_response` function."""

    def tearDown(self):
        # Clean up settings
        settings.MAINTENANCE_MODE_REDIRECT_URL = None
        settings.MAINTENANCE_MODE_TEMPLATE = "503.html"
        settings.MAINTENANCE_MODE_GET_CONTEXT = None

    def test_redirect(self):
        settings.MAINTENANCE_MODE_REDIRECT_URL = "http://redirect.example.cz/"

        response = http.get_maintenance_response(RequestFactory().get("/dummy/"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "http://redirect.example.cz/")

    def test_no_context(self):
        settings.MAINTENANCE_MODE_TEMPLATE = "503.html"
        settings.MAINTENANCE_MODE_GET_CONTEXT = None

        response = http.get_maintenance_response(RequestFactory().get("/dummy/"))

        self.assertContains(
            response,
            "django-maintenance-mode",
            status_code=settings.MAINTENANCE_MODE_STATUS_CODE,
        )
        self.assertIn("max-age=0", response["Cache-Control"])

    def test_custom_context(self):
        settings.MAINTENANCE_MODE_TEMPLATE = "503.html"
        settings.MAINTENANCE_MODE_GET_CONTEXT = "tests.functions.get_template_context"

        response = http.get_maintenance_response(RequestFactory().get("/dummy/"))

        self.assertContains(
            response,
            "django-maintenance-mode",
            status_code=settings.MAINTENANCE_MODE_STATUS_CODE,
        )
        self.assertIn("max-age=0", response["Cache-Control"])

    def test_invalid_context_function(self):
        settings.MAINTENANCE_MODE_GET_CONTEXT = "invalid.invalid-context-function"

        self.assertRaisesMessage(
            ImproperlyConfigured,
            "not a valid function",
            http.get_maintenance_response,
            RequestFactory().get("/dummy/"),
        )

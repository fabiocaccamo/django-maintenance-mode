import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, JsonResponse
from django.test import override_settings
from django.urls import reverse

from maintenance_mode import utils

from .base import MaintenanceModeTestCase


class MiddlewareTestCase(MaintenanceModeTestCase):
    def test_middleware_urls(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        url = reverse("maintenance_mode_off")
        request = self._get_anonymous_user_request(url)

        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        with self.settings(ROOT_URLCONF="tests.urls_not_configured"):
            response = self.middleware.process_request(request)
            self.assertMaintenanceResponse(response)

    def test_middleware_anonymous_user(self):
        self._reset_state()

        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE = False
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

    @override_settings(
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.sessions",
            "maintenance_mode",
        ],
        ROOT_URLCONF="tests.urls_admin",
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.common.CommonMiddleware",
            "maintenance_mode.middleware.MaintenanceModeMiddleware",
        ],
    )
    def test_middleware_ignore_admin_site(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        # admin url with slash
        request = self._get_superuser_request("/admin/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # admin url without slash
        request = self._get_superuser_request("/admin")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # non-admin url
        request = self._get_superuser_request("/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_admin_site_not_configured(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        # admin url
        request = self._get_superuser_request("/admin/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # non-admin url
        request = self._get_superuser_request("/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_ip_addresses(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (
            utils.get_client_ip_address(request),
        )
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_ip_addresses_get_client_ip_address(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")
        request.META["CLIENT_IP_ADDRESS_FIELD"] = "127.0.0.2"

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (
            request.META["CLIENT_IP_ADDRESS_FIELD"],
        )
        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = (
            "tests.functions.get_client_ip_address"
        )
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = (
            "tests.functions.get_client_ip_address_invalid"
        )
        get_client_ip_address_error = False
        try:
            response = self.middleware.process_request(request)
        except ImproperlyConfigured:
            get_client_ip_address_error = True
        self.assertEqual(get_client_ip_address_error, True)

        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = (
            "tests.tests_invalid.get_client_ip_address"
        )
        get_client_ip_address_error = False
        try:
            response = self.middleware.process_request(request)
        except ImproperlyConfigured:
            get_client_ip_address_error = True
        self.assertEqual(get_client_ip_address_error, True)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (
            utils.get_client_ip_address(request),
        )
        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = None
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None
        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_logout_authenticated_user(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = True
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        request = self._get_authenticated_user_request("/")
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        request = self._get_authenticated_user_request("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = False
        request = self._get_authenticated_user_request("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_logout_staff_user(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        # default (None): staff user inherits LOGOUT_AUTHENTICATED_USER behavior
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        settings.MAINTENANCE_MODE_LOGOUT_STAFF_USER = None
        request = self._get_staff_user_request("/")
        self.middleware.process_request(request)
        self.assertTrue(request.user.is_anonymous)

        # explicit False: staff user is not logged out
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        settings.MAINTENANCE_MODE_LOGOUT_STAFF_USER = False
        request = self._get_staff_user_request("/")
        self.middleware.process_request(request)
        self.assertTrue(request.user.is_authenticated)

        # explicit True: staff user is logged out
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_STAFF_USER = True
        request = self._get_staff_user_request("/")
        self.middleware.process_request(request)
        self.assertTrue(request.user.is_anonymous)

        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_STAFF_USER = None

    def test_middleware_logout_superuser(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        # default (None): superuser inherits LOGOUT_AUTHENTICATED_USER behavior
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        settings.MAINTENANCE_MODE_LOGOUT_SUPERUSER = None
        request = self._get_superuser_request("/")
        self.middleware.process_request(request)
        self.assertTrue(request.user.is_anonymous)

        # explicit False: superuser is not logged out
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        settings.MAINTENANCE_MODE_LOGOUT_SUPERUSER = False
        request = self._get_superuser_request("/")
        self.middleware.process_request(request)
        self.assertTrue(request.user.is_authenticated)

        # explicit True: superuser is logged out
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_SUPERUSER = True
        request = self._get_superuser_request("/")
        self.middleware.process_request(request)
        self.assertTrue(request.user.is_anonymous)

        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_SUPERUSER = None

    def test_middleware_ignore_anonymous_user(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_authenticated_user(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_authenticated_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_get_authenticated_user(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        settings.MAINTENANCE_MODE_IGNORE_STAFF = True

        # simulate a non-session authenticated request (eg. JWT):
        # request.user is anonymous, the custom function returns the staff user
        settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER = (
            "tests.functions.get_authenticated_user"
        )
        request = self._get_anonymous_user_request("/")
        request.META["AUTHENTICATED_USER_FIELD"] = "staff-user"
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        # the custom function returns None -> fallback to request.user
        request = self._get_anonymous_user_request("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # request without user (eg. auth middleware not installed)
        settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER = None
        request = self.request_factory.get("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # invalid function path
        settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER = (
            "tests.tests_invalid.get_authenticated_user"
        )
        request = self._get_anonymous_user_request("/")
        with self.assertRaises(ImproperlyConfigured):
            self.middleware.process_request(request)

        # path to a non-callable object
        settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER = (
            "tests.functions.NOT_A_FUNCTION"
        )
        request = self._get_anonymous_user_request("/")
        with self.assertRaises(ImproperlyConfigured):
            self.middleware.process_request(request)

        settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER = None
        settings.MAINTENANCE_MODE_IGNORE_STAFF = False

    def test_middleware_ignore_staff(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_staff_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_STAFF = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_STAFF = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_superuser(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_superuser_request("/")

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_tests(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_TESTS = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_TESTS = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_urls(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_URLS = ("/",)
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_URLS = (re.compile("/"),)
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_URLS = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_redirect_url(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_REDIRECT_URL = reverse("maintenance_mode_redirect")
        response = self.middleware.process_request(request)
        response.client = self.client
        self.assertRedirects(response, settings.MAINTENANCE_MODE_REDIRECT_URL)

        settings.MAINTENANCE_MODE_REDIRECT_URL = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_get_template_context(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        settings.MAINTENANCE_MODE_GET_CONTEXT = "tests.functions.get_template_context"
        response = self.client.get("/")
        val = response.context.get("TEST_MAINTENANCE_MODE_GET_CONTEXT", False)
        self.assertTrue(val)

        get_template_context_error = False
        try:
            settings.MAINTENANCE_MODE_GET_CONTEXT = (
                "tests.tests_invalid.get_template_context_invalid"
            )
            response = self.client.get("/")
            val = response.context.get("TEST_MAINTENANCE_MODE_GET_CONTEXT", False)
            self.assertFalse(val)
        except ImproperlyConfigured:
            get_template_context_error = True
        self.assertTrue(get_template_context_error)

        get_template_context_error = False
        try:
            settings.MAINTENANCE_MODE_GET_CONTEXT = (
                "tests.functions.get_template_context_invalid"
            )
            response = self.client.get("/")
            val = response.context.get("TEST_MAINTENANCE_MODE_GET_CONTEXT", False)
            self.assertFalse(val)
        except ImproperlyConfigured:
            get_template_context_error = True
        self.assertTrue(get_template_context_error)

        settings.MAINTENANCE_MODE_GET_CONTEXT = None
        response = self.client.get("/")
        val = response.context.get("TEST_MAINTENANCE_MODE_GET_CONTEXT", False)
        self.assertFalse(val)

    def test_middleware_response_type(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True
        request = self._get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_RESPONSE_TYPE = "none"
        with self.assertRaises(ImproperlyConfigured):
            self.middleware.process_request(request)

        settings.MAINTENANCE_MODE_RESPONSE_TYPE = "json"
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)
        self.assertTrue(isinstance(response, JsonResponse))

        settings.MAINTENANCE_MODE_RESPONSE_TYPE = "html"
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)
        self.assertTrue(isinstance(response, HttpResponse))

    def test_middleware_response_type_function(self):
        self._reset_state()

        settings.MAINTENANCE_MODE = True

        settings.MAINTENANCE_MODE_RESPONSE_TYPE = "tests.functions.get_response_type"
        request = self._get_anonymous_user_request("/api/test/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)
        self.assertTrue(isinstance(response, JsonResponse))

        request = self._get_anonymous_user_request("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)
        self.assertFalse(isinstance(response, JsonResponse))
        self.assertTrue(isinstance(response, HttpResponse))

        # function returning an invalid value
        settings.MAINTENANCE_MODE_RESPONSE_TYPE = (
            "tests.functions.get_response_type_invalid"
        )
        request = self._get_anonymous_user_request("/")
        with self.assertRaises(ImproperlyConfigured):
            self.middleware.process_request(request)

        # invalid function path
        settings.MAINTENANCE_MODE_RESPONSE_TYPE = (
            "tests.tests_invalid.get_response_type"
        )
        request = self._get_anonymous_user_request("/")
        with self.assertRaises(ImproperlyConfigured):
            self.middleware.process_request(request)

        settings.MAINTENANCE_MODE_RESPONSE_TYPE = "html"

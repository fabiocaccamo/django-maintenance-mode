import os
import re
import sys
from importlib import import_module
from io import StringIO
from tempfile import mkstemp
from unittest.mock import patch

import fsutil
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import HttpResponse, JsonResponse
from django.test import (
    Client,
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)
from django.urls import reverse

from maintenance_mode import backends, core, http, io, middleware, utils, views
from maintenance_mode.logging import RequireNotMaintenanceMode503
from maintenance_mode.management.commands.maintenance_mode import (
    Command as MaintenanceModeCommand,
)

from .views import force_maintenance_mode_off_view, force_maintenance_mode_on_view


class NotImplementedBackend(backends.AbstractStateBackend):
    pass


def get_client_ip_address(request):
    return request.META["CLIENT_IP_ADDRESS_FIELD"]


def get_template_context(request):
    return {"TEST_MAINTENANCE_MODE_GET_CONTEXT": True}


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "maintenance_mode.middleware.MaintenanceModeMiddleware",
    ],
    ROOT_URLCONF="tests.urls",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "maintenance_mode.context_processors.maintenance_mode",
                ],
            },
        },
    ],
)
class MaintenanceModeTestCase(TestCase):
    def setUp(self):
        self.anonymous_user = AnonymousUser()

        self.authenticated_user = User.objects.create_user(
            "authenticated-user", "authenticated@django-maintenance-mode.test", "test"
        )
        self.authenticated_user.save()

        self.staff_user = User.objects.create_user(
            "staff-user", "staff@django-maintenance-mode.test", "test"
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.superuser = User.objects.create_user(
            "superuser", "superuser@django-maintenance-mode.test", "test"
        )
        self.superuser.is_superuser = True
        self.superuser.save()

        self.client = Client()
        self.request_factory = RequestFactory()
        self.middleware = middleware.MaintenanceModeMiddleware()

        # use an existing directory as filepath to be sure that an OSError is raised
        self.invalid_file_path = fsutil.get_parent_dir(__file__)

        self.__reset_state()

    def tearDown(self):
        self.__reset_state()

    def assertMaintenanceResponse(self, response):
        self.assertTemplateUsed(settings.MAINTENANCE_MODE_TEMPLATE)
        self.assertTrue(response is not None)
        self.assertEqual(response.status_code, settings.MAINTENANCE_MODE_STATUS_CODE)

    def assertOkResponse(self, response):
        self.assertTrue(response is not None)
        self.assertEqual(response.status_code, 200)

    def __get_request_for_user_and_url(self, user, url):
        request = self.request_factory.get(url)
        request.user = user
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        request.session.save()
        return request

    def __get_anonymous_user_request(self, url):
        return self.__get_request_for_user_and_url(self.anonymous_user, url)

    def __get_authenticated_user_request(self, url):
        return self.__get_request_for_user_and_url(self.authenticated_user, url)

    def __get_staff_user_request(self, url):
        return self.__get_request_for_user_and_url(self.staff_user, url)

    def __get_superuser_request(self, url):
        return self.__get_request_for_user_and_url(self.superuser, url)

    def __login_staff_user(self):
        self.client.login(username="staff-user", password="test")

    def __login_superuser(self):
        self.client.login(username="superuser", password="test")

    def __logout(self):
        self.client.logout()

    def __reset_state(self):
        settings.MAINTENANCE_MODE = None
        core.set_maintenance_mode(False)
        try:
            os.remove(settings.MAINTENANCE_MODE_STATE_FILE_PATH)
        except OSError:
            pass

    def test_io(self):
        self.__reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH

        val = io.read_file(file_path)
        self.assertEqual(val, "")

        # ensure overwrite instead of append
        io.write_file(file_path, "test")
        io.write_file(file_path, "test")
        io.write_file(file_path, "test")
        val = io.read_file(file_path)
        self.assertEqual(val, "test")

    def test_io_invalid_file_path(self):
        self.__reset_state()

        file_path = self.invalid_file_path

        self.assertRaises((IOError, OSError), io.write_file, file_path, "test")
        self.assertRaises((IOError, OSError), io.read_file, file_path)

    def test_backend_local_file(self):
        self.__reset_state()

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

    def test_backend_local_file_invalid_values(self):
        self.__reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        io.write_file(file_path, "test")
        backend = core.get_maintenance_mode_backend()
        self.assertRaises(ValueError, backend.get_value)
        self.assertRaises(ValueError, backend.set_value, 2)
        self.assertRaises(ValueError, backend.set_value, "test")

    def test_backend_default_storage(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.DefaultStorageBackend"
        )

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.LocalFileBackend"
        )

    def test_backend_static_storage(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.StaticStorageBackend"
        )
        settings.STATIC_URL = "/static/"
        settings.STATIC_ROOT = "static"

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.LocalFileBackend"
        )

    def test_backend_cache(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.CacheBackend"
        )
        settings.CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "default",
            }
        }

        backend = core.get_maintenance_mode_backend()
        self.assertEqual(backend.get_value(), False)

        backend.set_value(True)
        self.assertEqual(backend.get_value(), True)

        backend.set_value(False)
        self.assertEqual(backend.get_value(), False)

        # test with default MAINTENANCE_MODE_STATE_BACKEND_FALLBACK_VALUE setting
        with patch("maintenance_mode.backends.cache") as mock_cache:
            mock_cache.get.side_effect = Exception
            mock_cache.set.side_effect = Exception
            backend.set_value(False)
            self.assertEqual(backend.get_value(), False)

        # test with MAINTENANCE_MODE_STATE_BACKEND_FALLBACK_VALUE set to True
        settings.MAINTENANCE_MODE_STATE_BACKEND_FALLBACK_VALUE = True
        with patch("maintenance_mode.backends.cache") as mock_cache:
            mock_cache.get.side_effect = Exception
            mock_cache.set.side_effect = Exception
            backend.set_value(False)
            self.assertEqual(backend.get_value(), True)

        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.backends.LocalFileBackend"
        )

    def test_backend_custom_invalid(self):
        self.__reset_state()

        backend = settings.MAINTENANCE_MODE_STATE_BACKEND

        # invalid module import
        settings.MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.NoBackend"
        self.assertRaises(ImproperlyConfigured, core.get_maintenance_mode_backend)

        # invalid module type (abstract base class)
        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.middleware.AbstractStateBackend"
        )
        self.assertRaises(ImproperlyConfigured, core.get_maintenance_mode_backend)

        # invalid implementation (methods not implemented)
        settings.MAINTENANCE_MODE_STATE_BACKEND = "tests.tests.NotImplementedBackend"
        self.assertRaises(
            NotImplementedError, core.get_maintenance_mode_backend().get_value
        )
        self.assertRaises(
            NotImplementedError, core.get_maintenance_mode_backend().set_value, 0
        )

        # invalid module type
        settings.MAINTENANCE_MODE_STATE_BACKEND = (
            "maintenance_mode.middleware.MaintenanceModeMiddleware"
        )
        self.assertRaises(ImproperlyConfigured, core.get_maintenance_mode_backend)

        settings.MAINTENANCE_MODE_STATE_BACKEND = backend

    def test_core(self):
        self.__reset_state()

        core.set_maintenance_mode(True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        core.set_maintenance_mode(False)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_core_invalid_file_path(self):
        self.__reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        settings.MAINTENANCE_MODE_STATE_FILE_PATH = self.invalid_file_path

        self.assertRaises((IOError, OSError), core.get_maintenance_mode)
        self.assertRaises((IOError, OSError), core.set_maintenance_mode, True)

        settings.MAINTENANCE_MODE_STATE_FILE_PATH = file_path

    def test_core_maintenance_enabled(self):
        self.__reset_state()

        core.set_maintenance_mode(False)
        settings.MAINTENANCE_MODE = True
        val = core.get_maintenance_mode()
        self.assertTrue(val)

    def test_core_maintenance_disabled(self):
        self.__reset_state()

        core.set_maintenance_mode(True)
        settings.MAINTENANCE_MODE = False
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_core_set_disabled(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        self.assertRaises(ImproperlyConfigured, core.set_maintenance_mode, True)

    def test_core_invalid_argument(self):
        self.__reset_state()

        io.write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, "not bool")
        self.assertRaises(ValueError, core.get_maintenance_mode)
        self.assertRaises(TypeError, core.set_maintenance_mode, "not bool")

    def test_logging_filter(self):
        self.__reset_state()

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

    def test_management_commands(self):
        self.__reset_state()

        call_command("maintenance_mode", "on")
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command("maintenance_mode", "off")
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_management_commands_invalid_file_path(self):
        self.__reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH
        settings.MAINTENANCE_MODE_STATE_FILE_PATH = self.invalid_file_path

        with self.assertRaises((CommandError, OSError)):
            call_command("maintenance_mode", "on")

        with self.assertRaises((CommandError, OSError)):
            call_command("maintenance_mode", "off")

        with self.assertRaises((CommandError, OSError)):
            cmd = MaintenanceModeCommand()
            cmd.get_maintenance_mode()

        with self.assertRaises((CommandError, OSError)):
            cmd = MaintenanceModeCommand()
            cmd.set_maintenance_mode(True)

        settings.MAINTENANCE_MODE_STATE_FILE_PATH = file_path

    def test_management_commands_no_arguments(self):
        self.__reset_state()

        with self.assertRaises(CommandError):
            call_command("maintenance_mode")

    def test_management_commands_invalid_argument(self):
        self.__reset_state()

        with self.assertRaises(CommandError):
            call_command("maintenance_mode", "hello world")

    def test_management_commands_interactive(self):
        self.__reset_state()

        sys_stdin = sys.stdin

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "on", interactive=True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "on", interactive=True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "off", interactive=True)
        val = core.get_maintenance_mode()
        self.assertFalse(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("y")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "off", interactive=True)
        val = core.get_maintenance_mode()
        self.assertFalse(val)
        confirm_answer_file.close()

        confirm_answer_file = StringIO("n")
        sys.stdin = confirm_answer_file
        call_command("maintenance_mode", "on", interactive=True)
        val = core.get_maintenance_mode()
        self.assertFalse(val)
        confirm_answer_file.close()

        sys.stdin = sys_stdin

    def test_management_commands_verbose(self):
        self.__reset_state()

        call_command("maintenance_mode", "on", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command("maintenance_mode", "on", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command("maintenance_mode", "off", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        call_command("maintenance_mode", "off", verbosity=3)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_urls(self):
        self.__reset_state()

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
        self.__reset_state()

        self.__login_superuser()

        url = reverse("maintenance_mode_on")
        self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        url = reverse("maintenance_mode_off")
        self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        self.__logout()

    def test_context_processor(self):
        self.__reset_state()

        core.set_maintenance_mode(True)
        response = self.client.get("/")
        val = response.context.get("maintenance_mode", False)
        self.assertTrue(val)
        core.set_maintenance_mode(False)

    def test_views(self):
        self.__reset_state()

        url = reverse("maintenance_mode_on")
        request = self.__get_anonymous_user_request(url)
        views.maintenance_mode_on(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        url = reverse("maintenance_mode_off")
        request = self.__get_anonymous_user_request(url)
        views.maintenance_mode_off(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_views_superuser(self):
        self.__reset_state()

        url = reverse("maintenance_mode_on")
        request = self.__get_superuser_request(url)
        views.maintenance_mode_on(request)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        url = reverse("maintenance_mode_off")
        request = self.__get_superuser_request(url)
        views.maintenance_mode_off(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_decorators_with_middleware(self):
        self.__reset_state()

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
        self.__reset_state()

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

    def test_middleware_urls(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        url = reverse("maintenance_mode_off")
        request = self.__get_anonymous_user_request(url)

        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        with self.settings(ROOT_URLCONF="tests.urls_not_configured"):
            response = self.middleware.process_request(request)
            self.assertMaintenanceResponse(response)

    def test_middleware_anonymous_user(self):
        self.__reset_state()

        request = self.__get_anonymous_user_request("/")

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
        self.__reset_state()

        settings.MAINTENANCE_MODE = True

        # admin url with slash
        request = self.__get_superuser_request("/admin/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # admin url without slash
        request = self.__get_superuser_request("/admin")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # non-admin url
        request = self.__get_superuser_request("/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_admin_site_not_configured(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True

        # admin url
        request = self.__get_superuser_request("/admin/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        # non-admin url
        request = self.__get_superuser_request("/")

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_ip_addresses(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (
            utils.get_client_ip_address(request),
        )
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_ip_addresses_get_client_ip_address(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")
        request.META["CLIENT_IP_ADDRESS_FIELD"] = "127.0.0.2"

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (
            request.META["CLIENT_IP_ADDRESS_FIELD"],
        )
        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = (
            "tests.tests.get_client_ip_address"
        )
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = (
            "tests.tests.get_client_ip_address_invalid"
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
        self.__reset_state()

        settings.MAINTENANCE_MODE = True

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = True
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        request = self.__get_authenticated_user_request("/")
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = True
        request = self.__get_authenticated_user_request("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
        settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER = False
        request = self.__get_authenticated_user_request("/")
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_anonymous_user(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_authenticated_user(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_authenticated_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_staff(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_staff_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_STAFF = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_STAFF = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_superuser(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_superuser_request("/")

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_tests(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_IGNORE_TESTS = True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_TESTS = False
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_ignore_urls(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")

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
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")

        settings.MAINTENANCE_MODE_REDIRECT_URL = reverse("maintenance_mode_redirect")
        response = self.middleware.process_request(request)
        response.client = self.client
        self.assertRedirects(response, settings.MAINTENANCE_MODE_REDIRECT_URL)

        settings.MAINTENANCE_MODE_REDIRECT_URL = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceResponse(response)

    def test_middleware_get_template_context(self):
        self.__reset_state()

        settings.MAINTENANCE_MODE = True

        settings.MAINTENANCE_MODE_GET_CONTEXT = "tests.tests.get_template_context"
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
                "tests.tests.get_template_context_invalid"
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
        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request("/")

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


class TestOverrideMaintenanceMode(SimpleTestCase):
    """
    Test `override_maintenance_mode` decorator/context manager.
    """

    def setUp(self):
        dummy, self.tmp_dir = mkstemp()

    def tearDown(self):
        os.remove(self.tmp_dir)

    override_cases = (
        # Maintenance mode states: (environ, override, result)
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, False),
    )

    def test_context_manager_override(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for environ, override, result in self.override_cases:
                core.set_maintenance_mode(environ)
                with core.override_maintenance_mode(override):
                    self.assertEqual(core.get_maintenance_mode(), result)
                self.assertEqual(core.get_maintenance_mode(), environ)

    def test_decorator(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for environ, override, result in self.override_cases:
                core.set_maintenance_mode(environ)

                @core.override_maintenance_mode(override)
                def test_function():
                    self.assertEqual(core.get_maintenance_mode(), result)  # noqa: B023

                test_function()

    def test_context_manager_on(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for value in [True, False]:
                core.set_maintenance_mode(value)
                with core.maintenance_mode_on():
                    self.assertEqual(core.get_maintenance_mode(), True)
                self.assertEqual(core.get_maintenance_mode(), value)

    def test_context_manager_off(self):
        with self.settings(MAINTENANCE_MODE_STATE_FILE_PATH=self.tmp_dir):
            for value in [True, False]:
                core.set_maintenance_mode(value)
                with core.maintenance_mode_off():
                    self.assertEqual(core.get_maintenance_mode(), False)
                self.assertEqual(core.get_maintenance_mode(), value)


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
        settings.MAINTENANCE_MODE_GET_CONTEXT = "tests.tests.get_template_context"

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

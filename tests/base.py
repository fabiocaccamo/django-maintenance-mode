import os
from importlib import import_module

import fsutil
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase, override_settings

from maintenance_mode import core, middleware


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

        self._reset_state()

    def tearDown(self):
        self._reset_state()

    def assertMaintenanceResponse(self, response):
        self.assertTemplateUsed(settings.MAINTENANCE_MODE_TEMPLATE)
        self.assertTrue(response is not None)
        self.assertEqual(response.status_code, settings.MAINTENANCE_MODE_STATUS_CODE)

    def assertOkResponse(self, response):
        self.assertTrue(response is not None)
        self.assertEqual(response.status_code, 200)

    def _get_request_for_user_and_url(self, user, url):
        request = self.request_factory.get(url)
        request.user = user
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore()
        request.session.save()
        return request

    def _get_anonymous_user_request(self, url):
        return self._get_request_for_user_and_url(self.anonymous_user, url)

    def _get_authenticated_user_request(self, url):
        return self._get_request_for_user_and_url(self.authenticated_user, url)

    def _get_staff_user_request(self, url):
        return self._get_request_for_user_and_url(self.staff_user, url)

    def _get_superuser_request(self, url):
        return self._get_request_for_user_and_url(self.superuser, url)

    def _login_staff_user(self):
        self.client.login(username="staff-user", password="test")

    def _login_superuser(self):
        self.client.login(username="superuser", password="test")

    def _logout(self):
        self.client.logout()

    def _reset_state(self):
        settings.MAINTENANCE_MODE = None
        core.set_maintenance_mode(False)
        try:
            os.remove(settings.MAINTENANCE_MODE_STATE_FILE_PATH)
        except OSError:
            pass

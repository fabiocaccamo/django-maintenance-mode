# -*- coding: utf-8 -*-

import django
from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, RequestFactory, TestCase, override_settings

if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

from maintenance_mode import core, io, middleware, settings, views

import os
import re


def get_template_context(request):
    return { 'TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT':True }

def custom_ip_getter(request):
    return request.META['CUSTOM_IP_FIELD']


@override_settings(
    MIDDLEWARE_CLASSES = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',

        'maintenance_mode.middleware.MaintenanceModeMiddleware',
    ],
    ROOT_URLCONF = 'tests.urls',

    #for django < 1.8
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.request',
        'maintenance_mode.context_processors.maintenance_mode',
    ),

    #for django >= 1.8
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'maintenance_mode.context_processors.maintenance_mode',
                ],
            },
        },
    ]
)
class MaintenanceModeTestCase(TestCase):

    def setUp(self):

        self.anonymous_user = AnonymousUser

        self.staff_user = User.objects.create_user('staff-user', 'staff@django-maintenance-mode.test', 'test')
        self.staff_user.is_staff=True
        self.staff_user.save()

        self.superuser = User.objects.create_user('superuser', 'superuser@django-maintenance-mode.test', 'test')
        self.superuser.is_superuser=True
        self.superuser.save()

        self.client = Client()
        self.request_factory = RequestFactory()
        self.middleware = middleware.MaintenanceModeMiddleware()

        self.__reset_state()

    def tearDown(self):

        self.__reset_state()

    def assertMaintenanceMode(self, response):

        self.assertTemplateUsed(settings.MAINTENANCE_MODE_TEMPLATE)

        if django.VERSION >= (1, 8):

            self.assertEqual(response.status_code, 503)

    def __get_anonymous_user_request(self, url):
        request = self.request_factory.get(url)
        request.user = self.anonymous_user
        return request

    def __get_staff_user_request(self, url):
        request = self.request_factory.get(url)
        request.user = self.staff_user
        return request

    def __get_superuser_request(self, url):
        request = self.request_factory.get(url)
        request.user = self.superuser
        return request

    def __login_staff_user(self):
        self.client.login(username='staff-user', password='test')

    def __login_superuser(self):
        self.client.login(username='superuser', password='test')

    def __logout(self):
        self.client.logout()

    def __reset_state(self):

        settings.MAINTENANCE_MODE = False
        core.set_maintenance_mode(False)

        try:
            os.remove(settings.MAINTENANCE_MODE_STATE_FILE_PATH)

        except OSError:
            pass

    def test_io(self):

        self.__reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH

        val = io.read_file(file_path)
        self.assertEqual(val, '')

        val = io.write_file(file_path, 'test')
        self.assertTrue(val)

        #ensure overwrite instead of append
        val = io.write_file(file_path, 'test')
        val = io.write_file(file_path, 'test')
        val = io.read_file(file_path)
        self.assertEqual(val, 'test')

    def test_io_invalid_file_path(self):

        self.__reset_state()

        file_path = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ:/maintenance_mode_state.txt'

        val = io.write_file(file_path, 'test')
        self.assertFalse(val)

        val = io.read_file(file_path)
        self.assertEqual(val, '')

    def test_core(self):

        self.__reset_state()

        core.set_maintenance_mode(True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        core.set_maintenance_mode(False)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_core_invalid_argument(self):

        self.__reset_state()

        val = io.write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, 'not bool')
        self.assertTrue(val)
        self.assertRaises(ValueError, core.get_maintenance_mode)
        self.assertRaises(TypeError, core.set_maintenance_mode, 'not bool')

    def test_management_commands(self):

        self.__reset_state()

        call_command('maintenance_mode', 'on')
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command('maintenance_mode', 'off')
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_management_commands_no_arguments(self):

        command_error = False
        try:
            call_command('maintenance_mode')
        except CommandError:
            command_error = True
        self.assertTrue(command_error)

    def test_management_commands_invalid_argument(self):

        command_error = False
        try:
            call_command('maintenance_mode', 'hello world')
        except CommandError:
            command_error = True
        self.assertTrue(command_error)

    def test_management_commands_too_many_arguments(self):

        if django.VERSION < (1, 8):
            command_error = False
            try:
                call_command('maintenance_mode', 'on', 'off')
            except CommandError:
                command_error = True
            self.assertTrue(command_error)

    def test_urls(self):

        self.__reset_state()

        url = reverse('maintenance_mode_on')
        response = self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertRedirects(response, '/')
        self.assertFalse(val)

        url = reverse('maintenance_mode_off')
        response = self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertRedirects(response, '/')
        self.assertFalse(val)

    def test_urls_superuser(self):

        self.__reset_state()

        self.__login_superuser()

        url = reverse('maintenance_mode_on')
        response = self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        url = reverse('maintenance_mode_off')
        response = self.client.get(url)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        self.__logout()

    def test_context_processor(self):

        self.__reset_state()

        core.set_maintenance_mode(True)
        response = self.client.get('/')
        val = response.context.get('maintenance_mode', False)
        self.assertTrue(val)
        core.set_maintenance_mode(False)

    def test_views(self):

        self.__reset_state()

        url = reverse('maintenance_mode_on')
        request = self.__get_anonymous_user_request(url)
        views.maintenance_mode_on(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        url = reverse('maintenance_mode_off')
        request = self.__get_anonymous_user_request(url)
        views.maintenance_mode_off(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_views_superuser(self):

        self.__reset_state()

        url = reverse('maintenance_mode_on')
        request = self.__get_superuser_request(url)
        views.maintenance_mode_on(request)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        url = reverse('maintenance_mode_off')
        request = self.__get_superuser_request(url)
        views.maintenance_mode_off(request)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_middleware_urls(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE=True
        url = reverse('maintenance_mode_off')
        request = self.__get_anonymous_user_request(url)

        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        with self.settings(ROOT_URLCONF='tests.urls_not_configured'):
            response = self.middleware.process_request(request)
            self.assertMaintenanceMode(response)

    def test_middleware_anonymous_user(self):

        self.__reset_state()

        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE = True
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

        settings.MAINTENANCE_MODE = False
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

    def test_middleware_ignore_ip_addresses(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (request.META['REMOTE_ADDR'],)
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_ignore_ip_addresses_custom_ip_getter(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request('/')
        request.META['CUSTOM_IP_FIELD'] = '127.0.0.2'

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = (request.META['CUSTOM_IP_FIELD'],)
        settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = 'tests.tests.custom_ip_getter'
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_ignore_staff(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_staff_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_STAFF=True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_STAFF=False
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_ignore_superuser(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_superuser_request('/')

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER=True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER=False
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_ignore_test(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_TEST=True
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_TEST=False
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_ignore_urls(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_URLS = (re.compile('/'), )
        response = self.middleware.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_URLS = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_redirect_url(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_REDIRECT_URL = reverse('maintenance_mode_redirect')
        response = self.middleware.process_request(request)
        response.client = self.client
        if django.VERSION < (1, 9):
            self.assertEqual(response.url, settings.MAINTENANCE_MODE_REDIRECT_URL)
        else:
            self.assertRedirects(response, settings.MAINTENANCE_MODE_REDIRECT_URL)

        settings.MAINTENANCE_MODE_REDIRECT_URL = None
        response = self.middleware.process_request(request)
        self.assertMaintenanceMode(response)

    def test_middleware_template_context(self):

        self.__reset_state()

        settings.MAINTENANCE_MODE = True

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = 'tests.tests.get_template_context'
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertTrue(val)

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = 'tests.tests_invalid.get_template_context_invalid'
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertFalse(val)

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = 'tests.tests.get_template_context_invalid'
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertFalse(val)

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = None
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertFalse(val)


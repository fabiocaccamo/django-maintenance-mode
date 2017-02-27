# -*- coding: utf-8 -*-

import django
from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase, override_settings, modify_settings

if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

from maintenance_mode import core, io, middleware, settings, views

import re


def get_template_context(request):
    return { 'TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT':True }


class MaintenanceModeTestCase(TestCase):

    def setUp(self):

        self.anonymous_user = AnonymousUser
        self.staff_user = User.objects.create_user('staff-user', email='staff@django-maintenance-mode.test', password='test', is_staff=True)
        self.superuser = User.objects.create_superuser('superuser', email='superuser@django-maintenance-mode.test', password='test')
        self.client = Client()
        self.request_factory = RequestFactory()

    def tearDown(self):

        self.__reset_state();

    def assertMaintenanceMode(self, response):

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

    def __reset_state(self):

        core.set_maintenance_mode(False)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_io(self):

        self.__reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH

        val = io.write_file(file_path, 'test')
        self.assertTrue(val)

        val = io.read_file(file_path)
        self.assertEqual(val, 'test')

        file_path = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ:/maintenance_mode_state.txt'

        val = io.write_file(file_path, 'test')
        self.assertFalse(val)

        val = io.read_file(file_path)
        self.assertEqual(val, None)

    def test_core(self):

        self.__reset_state()

        val = io.write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, 'not bool')
        self.assertTrue(val)
        self.assertRaises(ValueError, core.get_maintenance_mode)
        self.assertRaises(TypeError, core.set_maintenance_mode, 'not bool')

        core.set_maintenance_mode(True)
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        core.set_maintenance_mode(False)
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    def test_management_commands(self):

        self.__reset_state()

        call_command('maintenance_mode', 'on')
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command('maintenance_mode', 'invalid argument')
        val = core.get_maintenance_mode()
        self.assertTrue(val)

        call_command('maintenance_mode', 'off')
        val = core.get_maintenance_mode()
        self.assertFalse(val)

        call_command('maintenance_mode', 'invalid argument')
        val = core.get_maintenance_mode()
        self.assertFalse(val)

    @override_settings(ROOT_URLCONF='maintenance_mode.tests_urls')
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

    @override_settings(TEMPLATES = [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'maintenance_mode.context_processors.maintenance_mode',
            ],
        },
    },])
    def test_context_processor(self):

        self.__reset_state()

        core.set_maintenance_mode(True)
        response = self.client.get('/')
        val = response.context['maintenance_mode']
        self.assertTrue(val)
        core.set_maintenance_mode(False)

    @override_settings(ROOT_URLCONF='maintenance_mode.tests_urls')
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

    @override_settings(ROOT_URLCONF='maintenance_mode.tests_urls')
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

    @override_settings(ROOT_URLCONF='maintenance_mode.tests_urls')
    def test_middleware(self):

        self.__reset_state()

        m = middleware.MaintenanceModeMiddleware()

        #settings.MAINTENANCE_MODE
        settings.MAINTENANCE_MODE=True
        request = self.__get_anonymous_user_request('/')
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        settings.MAINTENANCE_MODE=False
        request = self.__get_anonymous_user_request('/')
        response = m.process_request(request)
        self.assertEqual(response, None)

        #maintenance mode off anonymous user
        core.set_maintenance_mode(False)
        request = self.__get_anonymous_user_request('/')
        response = m.process_request(request)
        self.assertEqual(response, None)

        #maintenance mode on with anonymous user
        core.set_maintenance_mode(True)
        request = self.__get_anonymous_user_request('/')
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = request.META['REMOTE_ADDR']
        response = m.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = None
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_IGNORE_STAFF
        request = self.__get_staff_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_STAFF=True
        response = m.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_STAFF=False
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_IGNORE_SUPERUSER
        request = self.__get_superuser_request('/')

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER=True
        response = m.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_SUPERUSER=False
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_IGNORE_TEST
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_TEST=True
        response = m.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_TEST=False
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_IGNORE_URLS
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_IGNORE_URLS = (re.compile('/'), )
        response = m.process_request(request)
        self.assertEqual(response, None)

        settings.MAINTENANCE_MODE_IGNORE_URLS = None
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_REDIRECT_URL
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_REDIRECT_URL = reverse('maintenance_mode_redirect')
        response = m.process_request(request)
        response.client = self.client
        self.assertRedirects(response, settings.MAINTENANCE_MODE_REDIRECT_URL)

        settings.MAINTENANCE_MODE_REDIRECT_URL = None
        response = m.process_request(request)
        self.assertMaintenanceMode(response)

        #settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT
        request = self.__get_anonymous_user_request('/')

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = 'maintenance_mode.tests.get_template_context'
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertTrue(val)

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = 'maintenance_mode.tests_invalid.get_template_context_invalid'
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertFalse(val)

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = 'maintenance_mode.tests.get_template_context_invalid'
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertFalse(val)

        settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT = None
        response = self.client.get('/')
        val = response.context.get('TEST_MAINTENANCE_MODE_TEMPLATE_CONTEXT', False)
        self.assertFalse(val)


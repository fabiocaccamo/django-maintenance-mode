import re
import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_string

from maintenance_mode.core import get_maintenance_mode
from maintenance_mode.utils import get_client_ip_address


def get_maintenance_response(request):
    """
    Return a '503 Service Unavailable' maintenance response.
    """
    if settings.MAINTENANCE_MODE_REDIRECT_URL:
        return redirect(settings.MAINTENANCE_MODE_REDIRECT_URL)

    context = {}

    if settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT:
        try:
            get_request_context_func = import_string(
                settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT
            )
        except ImportError:
            raise ImproperlyConfigured(
                "settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT "
                "is not a valid function path."
            )

        context = get_request_context_func(request=request)

    kwargs = {"context": context}
    response = render(
        request,
        settings.MAINTENANCE_MODE_TEMPLATE,
        status=settings.MAINTENANCE_MODE_STATUS_CODE,
        **kwargs
    )
    response["Retry-After"] = settings.MAINTENANCE_MODE_RETRY_AFTER
    add_never_cache_headers(response)
    return response


def _need_maintenance_from_view(request):
    try:
        view_match = resolve(request.path)
        view_func = view_match[0]
        view_dict = view_func.__dict__

        view_force_maintenance_mode_off = view_dict.get(
            "force_maintenance_mode_off", False
        )
        if view_force_maintenance_mode_off:
            # view has 'force_maintenance_mode_off' decorator
            return False

        view_force_maintenance_mode_on = view_dict.get(
            "force_maintenance_mode_on", False
        )
        if view_force_maintenance_mode_on:
            # view has 'force_maintenance_mode_on' decorator
            return True

    except Resolver404:
        pass


def _need_maintenance_from_url(request):
    try:
        url_off = reverse("maintenance_mode_off")
        resolve(url_off)
        if url_off == request.path_info:
            return False
    except NoReverseMatch:
        # maintenance_mode.urls not added
        pass


def _need_maintenance_ignore_users(request):
    if not hasattr(request, "user"):
        return

    user = request.user

    if settings.MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER and user.is_anonymous:
        return False

    if settings.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER and user.is_authenticated:
        return False

    if settings.MAINTENANCE_MODE_IGNORE_STAFF and user.is_staff:
        return False

    if settings.MAINTENANCE_MODE_IGNORE_SUPERUSER and user.is_superuser:
        return False


def _need_maintenance_ignore_admin_site(request):
    if not settings.MAINTENANCE_MODE_IGNORE_ADMIN_SITE:
        return

    try:
        request_path = request.path if request.path else ""
        if not request_path.endswith("/"):
            request_path += "/"

        admin_url = reverse("admin:index")
        if request_path.startswith(admin_url):
            return False
    except NoReverseMatch:
        # admin.urls not added
        pass


def _need_maintenance_ignore_tests(request):
    if not settings.MAINTENANCE_MODE_IGNORE_TESTS:
        return

    is_testing = False

    if (len(sys.argv) > 0 and "runtests" in sys.argv[0]) or (
        len(sys.argv) > 1 and sys.argv[1] == "test"
    ):
        # python runtests.py | python manage.py test | python
        # setup.py test | django-admin.py test
        is_testing = True

    if is_testing:
        return False


def _need_maintenance_ignore_ip_addresses(request):
    if not settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:
        return

    if settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS:
        try:
            get_client_ip_address_func = import_string(
                settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS
            )
        except ImportError:
            raise ImproperlyConfigured(
                "settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS "
                "is not a valid function path."
            )
        else:
            client_ip_address = get_client_ip_address_func(request)
    else:
        client_ip_address = get_client_ip_address(request)

    for ip_address in settings.MAINTENANCE_MODE_IGNORE_IP_ADDRESSES:
        ip_address_re = re.compile(ip_address)
        if ip_address_re.match(client_ip_address):
            return False


def _need_maintenance_ignore_urls(request):
    if not settings.MAINTENANCE_MODE_IGNORE_URLS:
        return

    for url in settings.MAINTENANCE_MODE_IGNORE_URLS:
        if not isinstance(url, re.Pattern):
            url = str(url)
        url_re = re.compile(url)
        if url_re.match(request.path_info):
            return False


def _need_maintenance_redirects(request):
    if not settings.MAINTENANCE_MODE_REDIRECT_URL:
        return

    redirect_url_re = re.compile(settings.MAINTENANCE_MODE_REDIRECT_URL)

    if redirect_url_re.match(request.path_info):
        return False


def need_maintenance_response(request):
    """
    Tells if the given request needs a maintenance response or not.
    """

    value = _need_maintenance_from_view(request)
    if isinstance(value, bool):
        return value

    value = get_maintenance_mode()
    if not value:
        return value

    value = _need_maintenance_from_url(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_users(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_admin_site(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_tests(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_ip_addresses(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_ignore_urls(request)
    if isinstance(value, bool):
        return value

    value = _need_maintenance_redirects(request)
    if isinstance(value, bool):
        return value

    return True

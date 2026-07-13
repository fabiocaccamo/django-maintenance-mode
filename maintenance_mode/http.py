import re
import sys

from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.cache import add_never_cache_headers
from django.utils.module_loading import import_string

from maintenance_mode.core import get_maintenance_mode
from maintenance_mode.utils import get_client_ip_address


def get_maintenance_response_context(request):
    context = {}
    if settings.MAINTENANCE_MODE_GET_CONTEXT:
        try:
            get_request_context_func = import_string(
                settings.MAINTENANCE_MODE_GET_CONTEXT
            )
        except ImportError as error:
            raise ImproperlyConfigured(
                "settings.MAINTENANCE_MODE_GET_CONTEXT is not a valid function path."
            ) from error

        context = get_request_context_func(request=request)
    return context


def get_maintenance_response_type(request):
    """
    Return the maintenance response type ('html' or 'json') for the given request.
    """
    response_types = ("html", "json")
    response_type = settings.MAINTENANCE_MODE_RESPONSE_TYPE
    if response_type in response_types:
        return response_type
    # response type can be the path of a function that
    # will be called with the request and must return 'html' or 'json'
    try:
        get_response_type_func = import_string(response_type)
    except ImportError as error:
        raise ImproperlyConfigured(
            "settings.MAINTENANCE_MODE_RESPONSE_TYPE value must be "
            "'html', 'json' or a valid function path."
        ) from error
    response_type = get_response_type_func(request=request)
    if response_type not in response_types:
        raise ImproperlyConfigured(
            "settings.MAINTENANCE_MODE_RESPONSE_TYPE function "
            "return value must be 'html' or 'json'."
        )
    return response_type


def get_maintenance_response(request):
    """
    Return a '503 Service Unavailable' HTML or JSON response based on user preference.
    """
    if settings.MAINTENANCE_MODE_REDIRECT_URL:
        return redirect(settings.MAINTENANCE_MODE_REDIRECT_URL)

    response = None
    response_type = get_maintenance_response_type(request)
    if response_type == "html":
        response = get_maintenance_html_response(request)
    elif response_type == "json":
        response = get_maintenance_json_response(request)

    if settings.MAINTENANCE_MODE_RETRY_AFTER:
        response["Retry-After"] = settings.MAINTENANCE_MODE_RETRY_AFTER

    add_never_cache_headers(response)
    return response


def get_maintenance_html_response(request):
    """
    Return an HTML response for maintenance.
    """
    context = get_maintenance_response_context(request)
    response = render(
        request,
        settings.MAINTENANCE_MODE_TEMPLATE,
        status=settings.MAINTENANCE_MODE_STATUS_CODE,
        context=context,
    )
    return response


def get_maintenance_json_response(request):
    """
    Return a JSON response for maintenance.
    """
    context = get_maintenance_response_context(request)
    response = JsonResponse(
        context,
        status=settings.MAINTENANCE_MODE_STATUS_CODE,
    )
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


def _need_maintenance_logout_user(user):
    if not user.is_authenticated:
        return False
    logout_authenticated_user = settings.MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER
    logout_staff_user = settings.MAINTENANCE_MODE_LOGOUT_STAFF_USER
    logout_superuser = settings.MAINTENANCE_MODE_LOGOUT_SUPERUSER
    if user.is_superuser:
        if logout_superuser is not None:
            return logout_superuser
        return logout_authenticated_user
    if user.is_staff:
        if logout_staff_user is not None:
            return logout_staff_user
        return logout_authenticated_user
    return logout_authenticated_user


def _get_maintenance_authenticated_user(request):
    if settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER:
        try:
            get_authenticated_user_func = import_string(
                settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER
            )
        except ImportError as error:
            raise ImproperlyConfigured(
                "settings.MAINTENANCE_MODE_GET_AUTHENTICATED_USER "
                "is not a valid function path."
            ) from error
        user = get_authenticated_user_func(request=request)
        if user is not None:
            return user
    return getattr(request, "user", None)


def _need_maintenance_ignore_users(request):
    user = _get_maintenance_authenticated_user(request)
    if user is None:
        return

    if _need_maintenance_logout_user(user):
        logout(request)
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
        except ImportError as error:
            raise ImproperlyConfigured(
                "settings.MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS "
                "is not a valid function path."
            ) from error
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

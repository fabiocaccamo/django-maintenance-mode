from django.contrib.auth.models import User

from maintenance_mode import backends


class NotImplementedBackend(backends.AbstractStateBackend):
    pass


def get_client_ip_address(request):
    return request.META["CLIENT_IP_ADDRESS_FIELD"]


def get_template_context(request):
    return {"TEST_MAINTENANCE_MODE_GET_CONTEXT": True}


def get_response_type(request):
    return "json" if request.path_info.startswith("/api") else "html"


def get_response_type_invalid(request):
    return "xml"


def get_authenticated_user(request):
    username = request.META.get("AUTHENTICATED_USER_FIELD")
    return User.objects.filter(username=username).first() if username else None


NOT_A_FUNCTION = "not-a-function"

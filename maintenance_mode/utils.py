# -*- coding: utf-8 -*-

def get_client_ip_address(request):
    """
    Get the client IP Address.
    """
    return request.META['REMOTE_ADDR']

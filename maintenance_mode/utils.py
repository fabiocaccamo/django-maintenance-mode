# -*- coding: utf-8 -*-

def get_client_ip_address(request):
    return request.META['REMOTE_ADDR']

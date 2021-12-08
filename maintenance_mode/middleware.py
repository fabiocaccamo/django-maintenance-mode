# -*- coding: utf-8 -*-

from maintenance_mode.http import (
    get_maintenance_response, need_maintenance_response, )


class MaintenanceModeMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response is None and callable(self.get_response):
            response = self.get_response(request)
        return response

    def process_request(self, request):
        if need_maintenance_response(request):
            return get_maintenance_response(request)
        return None

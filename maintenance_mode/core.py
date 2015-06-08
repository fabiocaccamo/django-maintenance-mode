# -*- coding: utf-8 -*-

from django.core.cache import get_cache

from maintenance_mode import settings


def get_state():
    
    cache = get_cache('default')
    value = cache.get('maintenance_mode', False)
    cache.close()
    return value
    
    
def set_state(value):
    
    cache = get_cache('default')
    cache.set('maintenance_mode', value, settings.MAINTENANCE_MODE_TIMEOUT)
    cache.close()
    
    
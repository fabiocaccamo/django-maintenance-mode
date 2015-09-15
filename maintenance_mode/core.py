# -*- coding: utf-8 -*-

from maintenance_mode import settings


def get_maintenance_mode():
    
    try:
        handler = open(settings.MAINTENANCE_MODE_STATE_FILE_PATH, 'r+')
        value = int(handler.read())
    except IOError:
        # If the file doesn't exist we shouldn't throw this
        return False
    finally:
        handler.close()
    
    return value
    
    
def set_maintenance_mode(value):
    
    handler = open(settings.MAINTENANCE_MODE_STATE_FILE_PATH, 'w+')
    handler.write(str(int(value)))
    handler.close()
    
    

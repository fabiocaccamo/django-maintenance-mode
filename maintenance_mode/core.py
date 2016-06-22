# -*- coding: utf-8 -*-

from maintenance_mode import settings


def get_maintenance_mode():

    try:
        handler = open(settings.MAINTENANCE_MODE_STATE_FILE_PATH, 'r+')
        value = 0

        try:
            value = int(handler.read())

        except ValueError:
            pass

        handler.close()

        return value

    except IOError:

        return False


def set_maintenance_mode(value):

    handler = open(settings.MAINTENANCE_MODE_STATE_FILE_PATH, 'w+')
    handler.write(str(int(value)))
    handler.close()


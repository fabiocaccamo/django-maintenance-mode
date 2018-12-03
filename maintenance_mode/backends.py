# -*- coding: utf-8 -*-

from django.conf import settings

from maintenance_mode.io import read_file, write_file


class AbstractStateBackend(object):

    def get_value(self):
        raise NotImplementedError()

    def set_value(self, value):
        raise NotImplementedError()


class LocalFileBackend(AbstractStateBackend):

    def get_value(self):
        value = read_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, '0')
        if value not in ['0', '1']:
            raise ValueError('state file content value is not 0|1')
        value = bool(int(value))
        return value

    def set_value(self, value):
        value = str(int(value))
        if value not in ['0', '1']:
            raise ValueError('state file content value is not 0|1')
        write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, value)


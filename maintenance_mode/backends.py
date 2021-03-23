# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from maintenance_mode.io import read_file, write_file


class AbstractStateBackend(object):

    @staticmethod
    def from_bool_to_str_value(value):
        value = str(int(value))
        if value not in ['0', '1']:
            raise ValueError('state value is not 0|1')
        return value

    @staticmethod
    def from_str_to_bool_value(value):
        value = value.strip()
        if value not in ['0', '1']:
            raise ValueError('state value is not 0|1')
        value = bool(int(value))
        return value

    def get_value(self):
        raise NotImplementedError()

    def set_value(self, value):
        raise NotImplementedError()


class DefaultStorageBackend(AbstractStateBackend):

    def get_value(self):
        filename = settings.MAINTENANCE_MODE_STATE_FILE_NAME
        try:
            with default_storage.open(filename, 'r') as statefile:
                return self.from_str_to_bool_value(statefile.read())
        except IOError:
            return False

    def set_value(self, value):
        filename = settings.MAINTENANCE_MODE_STATE_FILE_NAME
        if default_storage.exists(filename):
            default_storage.delete(filename)
        content = ContentFile(self.from_bool_to_str_value(value))
        default_storage.save(filename, content)


class LocalFileBackend(AbstractStateBackend):

    def get_value(self):
        value = read_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, '0')
        value = self.from_str_to_bool_value(value)
        return value

    def set_value(self, value):
        value = self.from_bool_to_str_value(value)
        write_file(settings.MAINTENANCE_MODE_STATE_FILE_PATH, value)

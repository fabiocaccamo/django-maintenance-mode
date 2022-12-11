from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from maintenance_mode.io import read_file, write_file


class AbstractStateBackend(object):
    @staticmethod
    def from_bool_to_str_value(value):
        value = str(int(value))
        if value not in ["0", "1"]:
            raise ValueError("state value is not 0|1")
        return value

    @staticmethod
    def from_str_to_bool_value(value):
        value = value.strip()
        if value not in ["0", "1"]:
            raise ValueError("state value is not 0|1")
        value = bool(int(value))
        return value

    def get_value(self):
        raise NotImplementedError()

    def set_value(self, value):
        raise NotImplementedError()


class DefaultStorageBackend(AbstractStateBackend):
    """
    django-maintenance-mode backend which uses the default storage.
    Kindly provided by Dominik George https://github.com/Natureshadow
    """

    def _get_filename(self):
        return settings.MAINTENANCE_MODE_STATE_FILE_NAME

    def get_value(self):
        filename = self._get_filename()
        try:
            with default_storage.open(filename, "r") as statefile:
                return self.from_str_to_bool_value(statefile.read())
        except IOError:
            return False

    def set_value(self, value):
        filename = self._get_filename()
        if default_storage.exists(filename):
            default_storage.delete(filename)
        content = ContentFile(self.from_bool_to_str_value(value).encode())
        default_storage.save(filename, content)


class StaticStorageBackend(AbstractStateBackend):
    """
    django-maintenance-mode backend which uses the staticfiles storage.
    """

    def get_value(self):
        filename = settings.MAINTENANCE_MODE_STATE_FILE_NAME
        if staticfiles_storage.exists(filename):
            with staticfiles_storage.open(filename, "r") as statefile:
                return self.from_str_to_bool_value(statefile.read())
        return False

    def set_value(self, value):
        filename = settings.MAINTENANCE_MODE_STATE_FILE_NAME
        if staticfiles_storage.exists(filename):
            staticfiles_storage.delete(filename)
        content = ContentFile(self.from_bool_to_str_value(value).encode())
        staticfiles_storage.save(filename, content)


class LocalFileBackend(AbstractStateBackend):
    """
    django-maintenance-mode backend which uses the local file-sistem.
    """

    def _get_filepath(self):
        return f"{settings.MAINTENANCE_MODE_STATE_FILE_PATH}"

    def get_value(self):
        value = read_file(self._get_filepath(), "0")
        value = self.from_str_to_bool_value(value)
        return value

    def set_value(self, value):
        value = self.from_bool_to_str_value(value)
        write_file(self._get_filepath(), value)

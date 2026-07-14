from django.conf import settings

from maintenance_mode import io

from .base import MaintenanceModeTestCase


class IOTestCase(MaintenanceModeTestCase):
    def test_io(self):
        self._reset_state()

        file_path = settings.MAINTENANCE_MODE_STATE_FILE_PATH

        val = io.read_file(file_path)
        self.assertEqual(val, "")

        # ensure overwrite instead of append
        io.write_file(file_path, "test")
        io.write_file(file_path, "test")
        io.write_file(file_path, "test")
        val = io.read_file(file_path)
        self.assertEqual(val, "test")

    def test_io_invalid_file_path(self):
        self._reset_state()

        file_path = self.invalid_file_path

        self.assertRaises((IOError, OSError), io.write_file, file_path, "test")
        self.assertRaises((IOError, OSError), io.read_file, file_path)

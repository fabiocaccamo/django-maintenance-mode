# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.22.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.22.0) - 2025-04-03
-   Add `Python 3.13` and `Django 5.1` / `Django 5.2` support.
-   Drop `Python 3.8`, `Python 3.9` and `Django 3.x` support.
-   Fix `manage.py maintenance_mode on/off` changes permissions of state file. #172
-   Bump requirements and `pre-commit` hooks.

## [0.21.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.21.1) - 2024-01-24
-   Fix `manage.py maintenance_mode on/off` changes permissions of state file. #172
-   Bump requirements and `pre-commit` hooks.

## [0.21.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.21.0) - 2023-12-11
-   Add `MAINTENANCE_MODE_LOGOUT_AUTHENTICATED_USER` setting support. #139
-   Add `MAINTENANCE_MODE_RESPONSE_TYPE` (`html` or `json`) setting support. #160
-   Renamed `settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT` to `settings.MAINTENANCE_MODE_GET_CONTEXT`.
-   Write state file atomically in `maintenance_mode.backends.LocalFileBackend`. #162
-   Set maintenance mode response `Retry-After` only if `MAINTENANCE_MODE_RETRY_AFTER` setting is not `0` or `None`.
-   Replace `black` and `isort` with `ruff-format`.
-   Bump requirements.
-   Bump `pre-commit` hooks.

## [0.20.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.20.0) - 2023-12-05
-   Add `Python 3.12` support.
-   Add `Django 5.0` support.
-   Speed-up test workflow.
-   Bump requirements.
-   Bump `pre-commit` hooks.

## [0.19.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.19.0) - 2023-10-03
-   Add cache backend (`"maintenance_mode.backends.CacheBackend"`). #153 (by [@epicserve](https://github.com/epicserve) in #154)
-   Bump requirements, Github actions and pre-commit hooks.

## [0.18.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.18.0) - 2022-12-12
-   Drop `Python < 3.8` and `Django < 2.2` support. #99
-   Add backend for using default static storage (`"maintenance_mode.backends.StaticStorageBackend"`). (by [@matmair](https://github.com/matmair) in #97)
-   Replace `str.format` with `f-strings`.
-   Replace `setup.py test` in favor of `runtests.py`.
-   Bump requirements, Github actions and pre-commit hooks.

## [0.17.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.17.1) - 2022-11-22
-   Add `Python 3.11` support.
-   Add `Django 4.1` support.
-   Add `pre-commit`.
-   Bump GitHub actions.
-   Improve `maintenance_mode.backends` extendibility.
-   Fix `settings.MAINTENANCE_MODE_STATE_FILE_PATH` not working with `pathlib.Path` value. #96

## [0.16.3](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.16.3) - 2022-04-19
-   Fixed default storage incompatibility with `s3` storage. #85 (thanks to [@Natureshadow](https://github.com/Natureshadow))

## [0.16.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.16.2) - 2021-12-08
-   Added `python 3.10` and `django 4.0` compatibility.

## [0.16.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.16.1) - 2021-09-24
-   Fixed logging filter condition to disable emailing 503 errors to admins while maintenance mode is enabled. #72
-   Added `python 3.9` and `django 3.2` to `tox` and `travis`.
-   Added docstring to `backends`, fixed miscellaneous typo.
-   Removed outdated `CONTEXT_PROCESSORS` reference from installation instructions.

## [0.16.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.16.0) - 2021-11-23
-   Added `maintenance_mode.backends.DefaultStorageBackend`.
-   Added `maintenance_mode.logging.RequireNotMaintenanceMode503` logging filter. #72
-   Fixed leading `/` in `settings.MAINTENANCE_MODE_STATE_FILE_PATH`. #76

## [0.15.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.15.1) - 2020-11-21
-   Fixed state file content with extra white-space. #71

## [0.15.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.15.0) - 2020-09-03
-   Added `maintenance_mode_on` and `maintenance_mode_off` context managers.
-   Added django 3.1 compatibility.

## [0.14.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.14.0) - 2019-12-03
-   Added python 3.8 and django 3.0 compatibility.

## [0.13.3](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.13.3) - 2019-07-01
-   Removed python 3.4 from travis.

## [0.13.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.13.2) - 2019-06-28
-   Added django 2.2 compatibility.

## [0.13.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.13.1) - 2019-03-07
-   Added `Retry-After` header and relative setting.

## [0.13.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.13.0) - 2018-12-21
-   Added `MAINTENANCE_MODE_STATUS_CODE` setting.

## [0.12.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.12.0) - 2018-12-03
-   Added pluggable backends support.

## [0.11.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.11.0) - 2018-10-08
-   Added python 3.7 and django 2.1 support.
-   Respect default content type (charset).
-   Improved tests coverage.

## [0.10.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.10.0) - 2018-05-31
-   Sorted imports alphabetically.
-   Added `MAINTENANCE_MODE_IGNORE_ADMIN_SITE` setting.
-   Added maintenance mode override.

## [0.9.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.9.1) - 2018-05-16
-   Fixed #43 - verbose turn on interactive mode. Command now raises `CommandError` instead of `IOError` when unable to read/write state file.

## [0.9.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.9.0) - 2018-03-29
-   Added `force_maintenance_mode_on` and `force_maintenance_mode_off` decorators.
-   Added `MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER` and `MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER` settings.

## [0.8.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.8.0) - 2018-03-19
-   Fixed #32 - default state file location.
-   Fixed #35 - don't silence errors when the state file can't be created.
-   Added Django 1.11 and Django 2.0 compatibility.

## [0.7.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.7.2) - 2018-02-21
-   Added verbosity option support to `maintenance_mode` command.

## [0.7.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.7.1) - 2018-02-20
-   Allowed regex in `settings.MAINTENANCE_MODE_IGNORE_URLS`.


## [0.7.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.7.0) - 2017-12-15
-   Added django 2.0 compatibility.

## [0.6.7](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.7) - 2017-12-15
-   Resolved import issue for Python3.
-   Added Requirements Status badge.

## [0.6.6](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.6) - 2017-10-13
-   Integrated `MAINTENANCE_MODE` setting into core.

## [0.6.5](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.5) - 2017-10-02
-   Improved pep8 compliance.
-   Added code quality badge.

## [0.6.4](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.4) - 2017-08-28
-   Fixed #27 - Removed `import_function`.

## [0.6.3](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.3) - 2017-04-20
-   Fixed #22.

## [0.6.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.2) - 2017-04-14
-   Added django 1.11 support.
-   Added python versions and license badges.

## [0.6.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.1) - 2017-03-22
-   Added classifiers and license to `setup.py`.

## [0.6.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.6.0) - 2017-03-20
-   Added `MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS` setting support.
-   Renamed `settings.MAINTENANCE_MODE_TEMPLATE_CONTEXT` to `settings.MAINTENANCE_MODE_GET_TEMPLATE_CONTEXT`.
-   Renamed `settings.MAINTENANCE_MODE_IGNORE_TEST` to `settings.MAINTENANCE_MODE_IGNORE_TESTS`.
-   Added python 3.6 compatibility.
-   Added coverage badge.
-   Added codecov to tox.

## [0.5.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.5.2) - 2017-03-09
-   Added coverage to tox.
-   Improved tests coverage to 100%.
-   Replaced `print` with `CommandError` in case of command called with invalid arguments.

## [0.5.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.5.1) - 2017-03-02
-   Fixed `io.read_file` return value if file not exists.
-   Added tox and .travis.
-   Moved tests outside app package.

## [0.5.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.5.0) - 2017-02-27
-   Added tests.
-   Updated middleware and added setting to ignore tests.
-   Added django 1.10 commands compatibility.

## [0.4.6](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.6) - 2017-02-13
-   Fixed #16 - django 1.10 middleware compliant.

## [0.4.5](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.5) - 2016-11-03
-   Fixed #14 - Added the possibility to configure `settings.MAINTENANCE_MODE_STATE_FILE_PATH`.

## [0.4.4](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.4) - 2016-10-10
-   Fixed #13 - Default context is missing in templates when maintenance mode is on in Django 1.9.

## [0.4.3](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.3) - 2016-10-07
-   Fixed #12 - No longer compatible with Django < 1.8 since release 0.3.3.

## [0.4.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.2) - 2016-10-03
-   Fixed #11 - Added no cache headers to response.

## [0.4.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.1) - 2016-09-10
-   Added `maintenance_mode` context processor.
-   Added django 1.10 compatibility.

## [0.4.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.4.0) - 2016-08-30
-   Fixed `django.conf.urls.patterns` warning.

## [0.3.5](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.3.5) - 2016-08-24
-   Fixed missing import.

## [0.3.4](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.3.4) - 2016-08-18
-   Fixed #5 - `NoReverseMatch` exception if `maintenance_mode.urls` was not added to urlpatterns.

## [0.3.3](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.3.3) - 2016-08-10
-   Added 503 status to response.

## [0.3.2](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.3.2) - 2016-06-22
-   Added capability to pass any context to the template.
-   Updated urls for django 1.9 compatibility.

## [0.3.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.3.1) - 2015-09-15
-   Fixed `UnboundLocalError`.
-   Added `/maintenance-mode/on/` and `/maintenance-mode/off/` urls support.

## [0.2.1](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.2.1) - 2015-09-15
-   Added error catch if there's no file to check in `get_maintenance_mode`.
-   Changed License to MIT.

## [0.2.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.2.0) - 2015-06-09
-   Added `MAINTENANCE_MODE_IGNORE_IP_ADDRESSES` setting support.
-   Added `MAINTENANCE_MODE_REDIRECT_URL` setting support.
-   Added `setup.py` and `setup.cfg`

## [0.1.0](https://github.com/fabiocaccamo/django-maintenance-mode/releases/tag/0.1.0) - 2015-06-08
-   Added sources.

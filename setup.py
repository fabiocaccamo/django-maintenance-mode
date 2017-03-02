
#!/usr/bin/env python
from setuptools import setup, find_packages

exec(open('maintenance_mode/version.py').read())

setup(
    name='django-maintenance-mode',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    version=__version__,
    description='django-maintenance-mode shows a 503 error page when maintenance-mode is on.',
    author='Fabio Caccamo',
    author_email='fabio.caccamo@gmail.com',
    url='https://github.com/fabiocaccamo/django-maintenance-mode',
    download_url='https://github.com/fabiocaccamo/django-maintenance-mode/archive/%s.tar.gz' % __version__,
    keywords = ['django', 'maintenance', 'mode', 'offline', 'under', '503', 'service', 'temporarily', 'unavailable'],
    requires=['django(>=1.4)'],
    classifiers=[],
    test_suite='runtests.runtests'
)


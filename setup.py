
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
    requires=['django(>=1.7)'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
    ],
    license='MIT',
    test_suite='runtests.runtests'
)


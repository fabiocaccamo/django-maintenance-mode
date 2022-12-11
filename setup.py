#!/usr/bin/env python

import os
import sys

from setuptools import find_packages, setup

exec(open("maintenance_mode/version.py").read())

package_name = "django-maintenance-mode"
package_url = f"https://github.com/fabiocaccamo/{package_name}"
package_path = os.path.abspath(os.path.dirname(__file__))
download_url = f"{package_url}/archive/{__version__}.tar.gz"
documentation_url = f"{package_url}#readme"
issues_url = f"{package_url}/issues"
sponsor_url = "https://github.com/sponsors/fabiocaccamo/"
twitter_url = "https://twitter.com/fabiocaccamo"

long_description_file_path = os.path.join(package_path, "README.md")
long_description_content_type = "text/markdown"
long_description = ""
try:
    with open(long_description_file_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except IOError:
    pass

setup(
    name=package_name,
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    version=__version__,
    description="django-maintenance-mode shows a 503 error page when maintenance-mode is on.",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author="Fabio Caccamo",
    author_email="fabio.caccamo@gmail.com",
    url=package_url,
    download_url=download_url,
    project_urls={
        "Documentation": documentation_url,
        "Issues": issues_url,
        "Funding": sponsor_url,
        "Twitter": twitter_url,
    },
    keywords=[
        "django",
        "maintenance",
        "mode",
        "offline",
        "under",
        "503",
        "service",
        "temporarily",
        "unavailable",
    ],
    requires=[
        "django (>= 2.2)",
    ],
    install_requires=[
        "python-fsutil >= 0.7.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
    ],
    license="MIT",
)

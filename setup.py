#!/usr/bin/env python
from os import path

from setuptools import setup, find_packages


name = 'celery-deduplicate'  # PyPI name
package_name = name.replace('-', '_')  # Python module name

here = path.dirname(path.abspath(__file__))

# Get the long description from the relevant file
long_description = None

try:
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    pass

setup(
    name=name,
    version='1.0b1',
    author='Joar Wandborg',
    author_email='joar@wandborg.se',
    license='MIT',
    description='deduplicate celery tasks',
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'celery'
    ]
)

# -*- encoding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages

assert sys.version_info >= (2, 7), "Python 2.7+ required."

current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, 'README.rst')) as readme_file:
    with open(os.path.join(current_dir, 'CHANGES.rst')) as changes_file:
        long_description = readme_file.read() + '\n' + changes_file.read()

sys.path.insert(0, current_dir + os.sep + 'src')
from ralph_scrooge import VERSION  # noqa
release = ".".join(str(num) for num in VERSION)

setup(
    name='ralph_scrooge',
    version=release,
    author='Grupa Allegro Sp. z o.o. and Contributors',
    author_email='it-ralph-dev@allegro.pl',
    description="Pricing module for Ralph",
    long_description=long_description,
    url='http://ralph.allegrogroup.com/',
    keywords='',
    platforms=['any'],
    license='Apache Software License v2.0',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    zip_safe=False,  # because templates are loaded from file path
    install_requires=[
        'dj.choices==0.11.0',
        'django-auth-ldap==1.2.8',
        'django-nose==1.4.4',
        'django-rq==0.9.3',
        'django-simple-history==1.8.1',
        'django==1.10.2',
        'djangorestframework==3.5.0',
        'factory-boy==2.3.1',
        'gunicorn==19.6.0',
        'ipaddr==2.1.11',
        'mock-django==0.6.6',
        'mock==0.8.0',
        'MySQL-python==1.2.3',
        'paramiko==1.9.0',
        'pyhermes>=0.1.2',
        'pymongo>=2.7.2',
        'python-dateutil==2.5.3',
        'python-novaclient==2.17.0',
        'pyyaml==3.12',
        'rq>=0.3.7',
        'SQLAlchemy==0.7.8',
        'django-filter==0.15.3',
        'ipaddress==1.0.17'
    ],
    entry_points={
        'django.pluggable_app': [
            'scrooge = ralph_scrooge.app:Scrooge',
        ],
        'scrooge.collect_plugins': [
            'scrooge = ralph_scrooge.plugins.collect',
        ],
        'console_scripts': [
            'scrooge = ralph_scrooge.__main__:prod',
            'dev_scrooge = ralph_scrooge.__main__:dev',
            'test_scrooge = ralph_scrooge.__main__:test',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ]
)

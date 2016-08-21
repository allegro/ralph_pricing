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
from ralph_scrooge import VERSION
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
        'django==1.4.21',
        'pymongo>=2.7.2',
        'python-novaclient==2.17.0',
        'django-simple-history==1.6.3',
        'djangorestframework==2.4.3',
        'django-filter==0.11',
        'django-bob==1.12.0',
        'django-nose>=1.3',
        'South==0.7.6',
        'djangorestframework==2.4.3',
        'django-rq==0.4.5',
        'bob-ajax-selects==1.6.1',
        'MySQL-python==1.2.3',
        'rq>=0.3.7',
        'rq-scheduler==0.3.6',
        'lck.django==0.8.10',
        'django-tastypie==0.9.16',
        'SQLAlchemy==0.7.8',
    ],
    entry_points={
        'django.pluggable_app': [
            'scrooge = ralph_scrooge.app:Scrooge',
        ],
        'scrooge.collect_plugins': [
            'scrooge = ralph_scrooge.plugins.collect',
        ],
        'console_scripts': [
            'ralph-scrooge = ralph_scrooge.__main__:main',
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

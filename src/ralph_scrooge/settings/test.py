#
# A testing profile.
#
from ralph_scrooge.settings.base import *  # noqa

import os
TEST_DATABASE_ENGINE = os.environ.get('TEST_DATABASE_ENGINE')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

if TEST_DATABASE_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'scrooge_test',
            'USER': 'root',
            'HOST': 'localhost',
        },
    }
elif TEST_DATABASE_ENGINE == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': 'postgres',
            'NAME': 'scrooge_test',
            'OPTIONS': {}
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'OPTIONS': {},
        }
    }

SOUTH_TESTS_MIGRATE = False

LOGGING['handlers']['file']['filename'] = 'scrooge.log'  # noqa

try:
    INSTALLED_APPS += ['django_nose']  # noqa
    TEST_RUNNER = str('django_nose.NoseTestSuiteRunner')
    NOSE_ARGS = ['--with-doctest', '-s']
except NameError:
    print('Cannot use nose test runner')

SKIP_MIGRATIONS = os.environ.get('SKIP_MIGRATIONS', None)
if SKIP_MIGRATIONS:
    print('skipping migrations')

    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "notmigrations"

    MIGRATION_MODULES = DisableMigrations()

INSTALLED_APPS += [
    'ralph_scrooge.tests'
]

# Redis & RQ
for queue in RQ_QUEUE_LIST + ('default',):
    RQ_QUEUES[queue]['ASYNC'] = False

try:
    execfile(os.path.expanduser("~/.scrooge/settings-test-scrooge-local"))  # noqa
except IOError:
    pass

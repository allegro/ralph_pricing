#
# A testing profile.
#
from ralph_scrooge.settings.base import *  # noqa

import os
TEST_DATABASE_NAME = os.environ.get('TEST_DATABASE_NAME', 'scrooge_test')
TEST_DATABASE_HOST = os.environ.get('TEST_DATABASE_HOST', 'localhost')
TEST_DATABASE_PORT = os.environ.get('TEST_DATABASE_PORT', 3306)
TEST_DATABASE_USER = os.environ.get('TEST_DATABASE_USER', 'root')
TEST_DATABASE_PASSWORD = os.environ.get('TEST_DATABASE_PASSWORD')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': TEST_DATABASE_NAME,
        'USER': TEST_DATABASE_USER,
        'HOST': TEST_DATABASE_HOST,
        'PORT': TEST_DATABASE_PORT,
        'PASSWORD': TEST_DATABASE_PASSWORD,
    },
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

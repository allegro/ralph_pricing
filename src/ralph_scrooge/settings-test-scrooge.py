#
# A testing profile.
#
import os

TEST_DATABASE_ENGINE = os.environ.get('TEST_DATABASE_ENGINE')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

if TEST_DATABASE_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ralph_test',
            'USER': 'root',
            'HOST': 'localhost',
        },
    }
elif TEST_DATABASE_ENGINE == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'USER': 'postgres',
            'NAME': 'ralph_test',
            'OPTIONS': {
                'autocommit': True,
            }
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

PLUGGABLE_APPS = ['assets', 'scrooge', 'cmdb']

SOUTH_TESTS_MIGRATE = False
try:
    INSTALLED_APPS += ('django_nose',)
    TEST_RUNNER = str('django_nose.NoseTestSuiteRunner')
    NOSE_ARGS = ['--with-doctest']
except NameError:
    print('Cannot use nose test runner')

try:
    execfile(os.path.expanduser("~/.ralph/settings-test-scrooge-local"))
except IOError:
    pass

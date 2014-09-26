#
# A testing profile.
#
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

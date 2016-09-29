import os

from ralph_scrooge.settings.base import *  # noqa

MEDIA_ROOT = os.path.expanduser('~/.scrooge/shared/uploads')
STATIC_ROOT = os.path.expanduser('~/.scrooge/shared/static')

INSTALLED_APPS += ('gunicorn',)  # noqa

try:
    execfile(os.path.expanduser("~/.scrooge/settings"))  # noqa
except IOError:
    pass

from ralph_scrooge.settings.base import *  # noqa

try:
    execfile(os.path.expanduser("~/.scrooge/settings"))  # noqa
except IOError:
    pass

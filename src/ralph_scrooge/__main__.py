#!/usr/bin/env python
import os
import sys


def main(settings_module='ralph_scrooge.settings', force=False):
    if force:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


def dev():
    main('ralph_scrooge.settings.dev')


def test():
    # test only with test settings, not local (or any set by environment
    # variable DJANGO_SETTINGS_MODULE) - especially usefull in vagrant, when
    # default DJANGO_SETTINGS_MODULE is overwrited in .profile
    main('ralph_scrooge.settings.test', force=True)


def prod():
    main('ralph_scrooge.settings.prod')


if __name__ == '__main__':
    main('ralph_scrooge.settings.prod')

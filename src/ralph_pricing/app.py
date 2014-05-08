# -*- coding: utf-8 -*-
"""The pluggable app definitions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.app import RalphModule


def setup_scrooge_logger(level='ERROR'):
    from django.conf import settings
    if 'raven.contrib.django' in settings.INSTALLED_APPS:
        from raven import Client
        from raven.handlers.logging import SentryHandler
        SCROOGE_SENTRY_DSN = getattr(settings, 'SCROOGE_SENTRY_DSN', False)
        if SCROOGE_SENTRY_DSN:
            client = Client(SCROOGE_SENTRY_DSN)
            handler = SentryHandler(client, level=level)
            logger = logging.getLogger('ralph_pricing')
            logger.addHandler(handler)
            return True
    return False


class Scrooge(RalphModule):
    """Scrooge main application. The 'ralph_pricing' name is retained
    internally for historical reasons, while we try to use 'scrooge' as
    displayed name."""

    url_prefix = 'scrooge'
    module_name = 'ralph_pricing'
    disp_name = 'Scrooge'
    icon = 'fugue-money-coin'

    def __init__(self, **kwargs):
        super(Scrooge, self).__init__(
            'ralph_pricing',
            distribution='scrooge',
            **kwargs
        )
        self.append_app()
        self.insert_templates(__file__)
        if not setup_scrooge_logger():
            self.register_logger('ralph_pricing', {
                'handlers': ['file'],
                'propagate': True,
                'level': 'DEBUG',
            })
            self.register_logger('ralph_pricing.plugins', {
                'handlers': ['file', 'console'],
                'propagate': True,
                'level': 'DEBUG',
            })
            self.register_logger('ralph_pricing.management', {
                'handlers': ['file', 'console'],
                'propagate': True,
                'level': 'DEBUG',
            })
        app_settings = {
            'SSH_NFSEN_CREDENTIALS': {},
            'NFSEN_CHANNELS': [],
            'NFSEN_CLASS_ADDRESS': [],
            'NFSEN_FILES_PATH': '',
            'VIRTUAL_VENTURE_NAMES': {},
            'WARNINGS_LIMIT_FOR_USAGES': 40,
            'CLOUD_UNKNOWN_VENTURE': None,
        }
        # workaround to not overwriting manually defined settings
        # check if setting is in global settings - if no, add default
        for key, value in app_settings.iteritems():
            if key not in self.settings:
                self.settings[key] = value

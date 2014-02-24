# -*- coding: utf-8 -*-
"""The pluggable app definitions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from raven import Client
from raven.handlers.logging import SentryHandler

from ralph.app import RalphModule


def setup_scrooge_logger(level='ERROR'):

    client = Client(
        'http://b4a72068092b475dba6917630417336f:8ee33fff77324953b26dda3cc5d2'
        'ec49@ralph-sentry.office/21',
    )
    handler = SentryHandler(client, level=level)
    logger = logging.getLogger('ralph_pricing')
    logger.addHandler(handler)

    # setup_logging(handler, exclude=['ralph'])


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
        setup_scrooge_logger()

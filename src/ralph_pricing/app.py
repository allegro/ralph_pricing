# -*- coding: utf-8 -*-
"""The pluggable app definitions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.app import RalphModule


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

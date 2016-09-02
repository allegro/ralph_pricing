# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


@plugin.register(
    chain='scrooge',
    requires=['ralph3_service_environment', 'ralph3_asset']
)
def ralph3_vip(today, **kwargs):
    pass

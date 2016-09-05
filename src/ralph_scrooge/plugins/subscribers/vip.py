# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph_scrooge.models.pricing_object import VIPInfo

from pyhermes.decorators import subscriber

logger = logging.getLogger(__name__)


@subscriber(
    topic='refreshVipEvent',
)
def ralph3_vip(event_data):
    print('=== OK! ===')

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin


logger = logging.getLogger(__name__)


@plugin.register(chain='usages')
def hamster_usages(**kwargs):
    logger.debug("Get hamster usage")
    usages = {}
    for venture in kwargs.get('ventures'):
        usages[venture.id] = {
            'hamster_usage_count': 3,
            'hamster_usage_cost': 0.3,
        }
    return usages


@plugin.register(chain='usages')
def hamster_schema(**kwargs):
    logger.debug("Get hamster usage")
    schema = OrderedDict()
    schema['hamster_usage_count'] = {
        'name': _("Hamster usage count"),
    }
    schema['hamster_usage_cost'] = {
        'name': _("Hamster usage cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

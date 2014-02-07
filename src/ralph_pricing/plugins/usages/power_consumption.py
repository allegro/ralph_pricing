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
def power_consumption_usages(**kwargs):
    logger.debug("Get power consumption usage")
    usages = {}
    for venture in kwargs.get('ventures'):
        usages[venture.id] = {
            'power_consumption_count': 5,
            'power_consumption_cost': 0.5,
        }
    return usages


@plugin.register(chain='usages')
def power_consumption_schema(**kwargs):
    logger.debug("Get power consumption schema")
    schema = OrderedDict()
    schema['power_consumption_count'] = {
        'name': _("Power consumption count"),
    }
    schema['power_consumption_cost'] = {
        'name': _("Power consumption cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

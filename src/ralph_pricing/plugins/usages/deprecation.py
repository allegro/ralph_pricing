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
def deprecation_usages(**kwargs):
    logger.debug("Get deprecation usage")
    assets_cost = 0.0
    usages = {}
    for venture in kwargs.get('ventures'):
        assets_cost += 0.1
        usages[venture.id] = {
            'assets_count': venture.venture_id,
            'assets_cost': assets_cost,
        }
    return usages


@plugin.register(chain='usages')
def deprecation_schema(**kwargs):
    logger.debug("Get deprecation schema")
    schema = OrderedDict()
    schema['assets_count'] = {
        'name': _("Assets count"),
    }
    schema['assets_cost'] = {
        'name': _("Assets cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

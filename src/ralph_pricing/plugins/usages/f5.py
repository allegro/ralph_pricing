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
def f5_usages(**kwargs):
    logger.debug("Get F5 usage")
    usages = {}
    for venture in kwargs.get('ventures'):
        usages[venture.id] = {
            'f5_requests_count': 2,
            'f5_requests_cost': 0.2,
        }
    return usages


@plugin.register(chain='usages')
def f5_schema(**kwargs):
    logger.debug("Get F5 schema")
    schema = OrderedDict()
    schema['f5_requests_count'] = {
        'name': _("F5 requests count"),
    }
    schema['f5_requests_cost'] = {
        'name': _("F5 requests cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

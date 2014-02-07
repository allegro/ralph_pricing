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
def splunk_usages(**kwargs):
    logger.debug("Splunk usage")
    usages = {}
    for venture in kwargs.get('ventures'):
        usages[venture.id] = {
            'splunk_usage_count': 6,
            'splunk_usage_cost': 0.6,
        }
    return usages


@plugin.register(chain='usages')
def splunk_schema(**kwargs):
    logger.debug("Splunk usage schema")
    schema = OrderedDict()
    schema['splunk_usage_count'] = {
        'name': _("Splunk usage count"),
    }
    schema['splunk_usage_cost'] = {
        'name': _("Splunk usage cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

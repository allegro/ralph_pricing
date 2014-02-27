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


# @plugin.register(chain='reports')
def f5_usages(**kwargs):
    """
    Return usages and costs for given ventures. Format of
    returned data must looks like:

    usages = {
        'venture_id': {
            'field_name': value,
            ...
        },
        ...
    }

    :returns dict: usages and costs
    :rtype dict:
    """
    logger.debug("Get F5 usage")
    usages = {}
    # TODO
    return usages


# @plugin.register(chain='reports')
def f5_schema(**kwargs):
    """
    Build schema for this usage. Format of schema looks like:

    schema = {
        'field_name': {
            'name': 'Verbous name',
            'next_option': value,
            ...
        },
        ...
    }

    :returns dict: schema for usage
    :rtype dict:
    """
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

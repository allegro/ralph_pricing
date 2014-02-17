# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin
from ralph_pricing.models import UsageType
from ralph_pricing.plugins.reports.utils import get_usages_and_costs


logger = logging.getLogger(__name__)


@plugin.register(chain='reports')
def splunk_usages(**kwargs):
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
    logger.debug("Splunk usage")
    usage_type = UsageType.objects.get(name='splunk')
    splunk_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )

    usages = defaultdict(lambda: defaultdict(int))
    for venture, splunk_usage in splunk_usages.iteritems():
        usages[venture]['splunk_usage_count'] = splunk_usage['value']
        usages[venture]['splunk_usage_cost'] = splunk_usage['cost']

    return usages


@plugin.register(chain='reports')
def splunk_schema(**kwargs):
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

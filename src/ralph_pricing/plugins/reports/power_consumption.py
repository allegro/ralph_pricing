# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict
from decimal import Decimal as D

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin
from ralph_pricing.models import UsageType, Warehouse
from ralph_pricing.plugins.reports.utils import get_usages_and_costs


logger = logging.getLogger(__name__)


@plugin.register(chain='reports')
def power_consumption_usages(**kwargs):
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
    """
    logger.debug("Get power consumption usage")

    usage_type = UsageType.objects.get(name='power_consumption')
    power_dc2_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
        Warehouse.objects.get(name='DC2'),
    )
    power_dc4_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
        Warehouse.objects.get(name='DC4'),
    )

    usages = defaultdict(lambda: defaultdict(int))
    for venture, power_dc2_usage in power_dc2_usages.iteritems():
        usages[venture]['power_consumption_count_dc2'] =\
            power_dc2_usage['value']
        usages[venture]['power_consumption_cost_dc2'] = power_dc2_usage['cost']
        if type(power_dc2_usage['cost']) in [int, float, type(D(0))]:
            usages[venture]['power_consumption_total_cost'] += \
                power_dc2_usage['cost']

    for venture, power_dc4_usage in power_dc4_usages.iteritems():
        usages[venture]['power_consumption_count_dc4'] =\
            power_dc4_usage['value']
        usages[venture]['power_consumption_cost_dc4'] = power_dc4_usage['cost']
        if type(power_dc4_usage['cost']) in [int, float, D]:
            usages[venture]['power_consumption_total_cost'] += \
                power_dc4_usage['cost']

    return usages


@plugin.register(chain='reports')
def power_consumption_schema(**kwargs):
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
    """
    logger.debug("Get power consumption schema")
    schema = OrderedDict()
    schema['power_consumption_count_dc2'] = {
        'name': _("Power consumption count (DC 2)"),
    }
    schema['power_consumption_cost_dc2'] = {
        'name': _("Power consumption cost (DC 2)"),
        'currency': True,
        'total_cost': True,
    }
    schema['power_consumption_count_dc4'] = {
        'name': _("Power consumption count (DC 4)"),
    }
    schema['power_consumption_cost_dc4'] = {
        'name': _("Power consumption cost (DC 4)"),
        'currency': True,
        'total_cost': True,
    }
    schema['power_consumption_total_cost'] = {
        'name': _("Power consumption total cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

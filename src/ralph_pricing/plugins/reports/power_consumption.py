# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from decimal import Decimal as D
from collections import OrderedDict, defaultdict

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin
from ralph_pricing.models import UsageType, Warehouse
from ralph_pricing.plugins.reports.utils import get_usages_and_costs


logger = logging.getLogger(__name__)


def get_warehouses():
    return Warehouse.objects.filter(show_in_report=True)

@plugin.register(chain='reports')
def power_consumption_usages(start, end, ventures, **kwargs):
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
    logger.debug("Get power consumption usage")

    usage_type = UsageType.objects.get(symbol='power_consumption')

    usages = defaultdict(lambda: defaultdict(int))
    for warehouse in get_warehouses():
        warehouse_name = "".join(warehouse.name.split(' ')).lower()
        power_usages = get_usages_and_costs(
            start,
            end,
            ventures,
            usage_type,
            warehouse,
        )
        for venture, power_usage in power_usages.iteritems():
            key_name = 'power_consumption_count_{0}'.format(warehouse_name)
            usages[venture][key_name] = power_usage['value']
            key_name = 'power_consumption_cost_{0}'.format(warehouse_name)
            usages[venture][key_name] = power_usage['cost']
            if type(power_usage['cost']) in [int, float, type(D(0))]:
                usages[venture]['power_consumption_total_cost'] += \
                    power_usage['cost']

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
    :rtype dict:
    """
    logger.debug("Get power consumption schema")

    schema = OrderedDict()
    for warehouse in get_warehouses():
        warehouse_name = "".join(warehouse.name.split(' ')).lower()
        schema['power_consumption_count_{0}'.format(warehouse_name)] = {
            'name': _("Power consumption count ({0})".format(warehouse_name)),
        }
        schema['power_consumption_cost_{0}'.format(warehouse_name)] = {
            'name': _("Power consumption cost ({0})".format(warehouse_name)),
            'currency': True,
        }
    schema['power_consumption_total_cost'] = {
        'name': _("Power consumption total cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

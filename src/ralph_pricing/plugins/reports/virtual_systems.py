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
def virtual_systems_usages(**kwargs):
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
    logger.debug("Get virtual systems usage")

    usage_type = UsageType.objects.get(name='virtual_disk_mb')
    disk_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )
    usage_type = UsageType.objects.get(name='virtual_memory_mb')
    memory_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )
    usage_type = UsageType.objects.get(name='virtual_cpu_cores')
    cpu_cores_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )

    usages = defaultdict(lambda: defaultdict(int))
    for venture, disk_usage in disk_usages.iteritems():
        usages[venture]['virtual_disk_count'] = disk_usage['value']
        usages[venture]['virtual_disk_cost'] = disk_usage['cost']
        if type(disk_usage['cost']) is not str:
            usages[venture]['virtual_systems_cost'] += disk_usage['cost']
    for venture, memory_usage in memory_usages.iteritems():
        usages[venture]['virtual_memory_count'] = memory_usage['value']
        usages[venture]['virtual_memory_cost'] = memory_usage['cost']
        if type(disk_usage['cost']) is not str:
            usages[venture]['virtual_systems_cost'] += memory_usage['cost']
    for venture, cpu_cores_usage in cpu_cores_usages.iteritems():
        usages[venture]['virtual_cpu_cores_count'] = cpu_cores_usage['value']
        usages[venture]['virtual_cpu_cores_cost'] = cpu_cores_usage['cost']
        if type(disk_usage['cost']) is not str:
            usages[venture]['virtual_systems_cost'] += cpu_cores_usage['cost']

    return usages


@plugin.register(chain='reports')
def virtual_systems_schema(**kwargs):
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
    logger.debug("Get virtual systems schema")
    schema = OrderedDict()
    schema['virtual_disk_count'] = {
        'name': _("Virtual disk MB count"),
    }
    schema['virtual_disk_cost'] = {
        'name': _("Virtual disk MB cost"),
        'currency': True,
    }
    schema['virtual_memory_count'] = {
        'name': _("Virtual memory MB count"),
    }
    schema['virtual_memory_cost'] = {
        'name': _("Virtual memory MB cost"),
        'currency': True,
    }
    schema['virtual_cpu_cores_count'] = {
        'name': _("Virtual CPU cores count"),
    }
    schema['virtual_cpu_cores_cost'] = {
        'name': _("Virtual CPU cores cost"),
        'currency': True,
    }
    schema['virtual_systems_cost'] = {
        'name': _("Virtual systems cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

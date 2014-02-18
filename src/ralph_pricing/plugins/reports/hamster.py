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
def hamster_usages(**kwargs):
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
    logger.debug("Get hamster usage")
    usage_type = UsageType.objects.get(symbol='hamster')
    hamster_usages = get_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )

    usages = defaultdict(lambda: defaultdict(int))
    for venture, hamster_usage in hamster_usages.iteritems():
        usages[venture]['hamster_usage_count'] = hamster_usage['value']
        usages[venture]['hamster_usage_cost'] = hamster_usage['cost']

    return usages


@plugin.register(chain='reports')
def hamster_schema(**kwargs):
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
    logger.debug("Get hamster schema")
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

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.db.models import Sum, Count
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.models import DailyDevice
from ralph.util import plugin


logger = logging.getLogger(__name__)


def get_assets_count_and_cost(start, end, ventures):
    """
    Returns sum of devices price and daily_costs for every venture in given
    time period

    :param datatime start: Begin of time interval for deprecation
    :param datatime end: End of time interval for deprecation
    :param list ventures: List of ventures
    :returns dict: query with selected devices for give venture
    :rtype dict:
    """
    assets_report_query = DailyDevice.objects.filter(
        pricing_device__is_virtual=False,
        date__gte=start,
        date__lte=end,
        pricing_venture__in=ventures,
    )

    assets_report = assets_report_query.values('pricing_venture')\
        .annotate(assets_price=Sum('price'))\
        .annotate(assets_cost=Sum('daily_cost'))\
        .annotate(assets_count=Count('id'))
    return assets_report


@plugin.register(chain='reports')
def deprecation_usages(start, end, ventures, **kwargs):
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
    logger.debug("Get deprecation usage")
    # TODO: calc blades
    report_days = (end - start).days + 1
    assets_count_and_cost = get_assets_count_and_cost(start, end, ventures)

    usages = {}
    for asset in assets_count_and_cost:
        usages[asset['pricing_venture']] = {
            'assets_count': asset['assets_count'] / report_days,
            'assets_cost': asset['assets_cost'],
        }
    return usages


@plugin.register(chain='reports')
def deprecation_schema(**kwargs):
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

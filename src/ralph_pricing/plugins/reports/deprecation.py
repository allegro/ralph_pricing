# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.db.models import Sum, Count
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.models import (
    DailyDevice,
)
from ralph.util import plugin


logger = logging.getLogger(__name__)


def get_assets_count_and_cost(start, end, ventures):
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


@plugin.register(chain='usages')
def deprecation_usages(**kwargs):
    logger.debug("Get deprecation usage")
    # TODO: calc blades
    report_days = (kwargs['end'] - kwargs['start']).days + 1
    assets_count_and_cost = get_assets_count_and_cost(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
    )

    usages = {}
    for asset in assets_count_and_cost:
        usages[asset['pricing_venture']] = {
            'assets_count': asset['assets_count'] / report_days,
            'assets_cost': asset['assets_cost'],
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

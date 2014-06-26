# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from collections import OrderedDict

from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.service import ServiceBasePlugin
from ralph_pricing.models import DailyUsage, UsagePrice

logger = logging.getLogger(__name__)


class CeilometerBasePlugin(ServiceBasePlugin):
    def costs(self, service, start, end, ventures, forecast=False, **kwargs):
        usage_types = service.usage_types.all()
        usages = DailyUsage.objects.filter(
            type__in=usage_types,
            date__gte=start,
            date__lte=end,
        )
        coin_ventures = {}
        for usage in usages:
            try:
                price = usage.type.usageprice_set.get(
                    start__lte=usage.date,
                    end__gte=usage.date,
                ).price
            except UsagePrice.DoesNotExist:
                price = 0
            venture = usage.pricing_venture.id
            val = float(usage.value) * float(price)
            coin_ventures[venture] = coin_ventures.get(venture, 0) + val
        res = dict([(v[0], {
            'ceilometer_cost': v[1],
        }) for v in coin_ventures.iteritems()])
        return res

    def schema(self, service, *args, **kwargs):
        schema = OrderedDict([
            ('ceilometer_cost', {
                'name': "Cloud 2.0 cost",
                'currency': True,
                'total_cost': True,
            }),
        ])
        return schema


@register(chain='reports')
class Ceilometer(CeilometerBasePlugin):
    pass

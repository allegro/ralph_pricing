# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from collections import defaultdict, OrderedDict
from decimal import Decimal as D

from django.db.models import Sum

from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.service import ServiceBasePlugin

logger = logging.getLogger(__name__)


class CeilometerBasePlugin(ServiceBasePlugin):
    def costs(self, service, start, end, ventures, forecast=False, **kwargs):
        logger.debug("Calculating report for service {0}".format(service))
        coin_ventures = defaultdict(D)
        usage_types = service.usage_types.all()

        for usage_type in usage_types:
            for usage_price in usage_type.usageprice_set.filter(
                start__lte=end,
                end__gte=start
            ):
                if forecast:
                    price = usage_price.forecast_price
                else:
                    price = usage_price.price
                up_start = max(start, usage_price.start)
                up_end = min(end, usage_price.end)

                ventures_usages = usage_type.dailyusage_set.filter(
                    date__gte=up_start,
                    date__lte=up_end,
                    pricing_venture__in=ventures,
                ).values('pricing_venture').annotate(value=Sum('value'))

                for usage in ventures_usages:
                    coin_ventures[usage['pricing_venture']] += (
                        D(usage['value']) * price
                    )

        res = dict([(v[0], {
            'ceilometer_cost': v[1],
        }) for v in coin_ventures.iteritems()])
        return res

    def schema(self, service, *args, **kwargs):
        schema = OrderedDict([
            ('ceilometer_cost', {
                'name': "{} cost".format(service.name),
                'currency': True,
                'total_cost': True,
            }),
        ])
        return schema


@register(chain='reports')
class Ceilometer(CeilometerBasePlugin):
    pass

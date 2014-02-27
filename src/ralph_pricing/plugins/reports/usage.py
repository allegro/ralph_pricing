# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict, OrderedDict
from decimal import Decimal as D

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from lck.cache import memoize

from ralph_pricing.models import DailyUsage, UsageType
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.base import BaseReportPlugin

logger = logging.getLogger(__name__)


class UsageBasePlugin(BaseReportPlugin):
    def _get_total_cost_by_warehouses(self, start, end, ventures, usage_type, forecast=False, **kwargs):
        """
        Returns total cost of usage for ventures
        """
        if usage_type.by_warehouse:
            warehouses = self.get_warehouses()
        else:
            warehouses = [None]
        result = []
        total_cost = D(0)
        for warehouse in warehouses:
            usage_in_warehouse = 0
            cost_in_warehouse = 0
            usage_prices = usage_type.usageprice_set.filter(
                start__lte=end,
                end__gte=start,
                type=usage_type,
            )
            if warehouse:
                usage_prices = usage_prices.filter(warehouse=warehouse)
            usage_prices = usage_prices.order_by('start')
            for usage_price in usage_prices:
                if forecast:
                    price = usage_price.forecast_price
                else:
                    price = usage_price.price
                if usage_type.by_cost:
                    price = self._get_price_from_cost(
                        usage_price,
                        forecast,
                        warehouse
                    )

                up_start = max(start, usage_price.start)
                up_end = min(end, usage_price.end)

                total_usage = self._get_total_usage_in_period(
                    up_start,
                    up_end,
                    usage_type,
                    warehouse,
                    ventures
                )
                usage_in_warehouse += total_usage
                cost = D(total_usage) * price
                cost_in_warehouse += cost

            result.append(usage_in_warehouse)
            cost_in_warehouse = D(cost_in_warehouse)
            result.append(cost_in_warehouse)
            total_cost += cost_in_warehouse
        if usage_type.by_warehouse:
            result.append(total_cost)
        return result

    def total_cost(self, *args, **kwargs):
        costs_by_wh = self._get_total_cost_by_warehouses(*args, **kwargs)
        return costs_by_wh[-1]

    def _get_usages_per_warehouse(self, usage_type, start, end, forecast, ventures):
        if usage_type.by_warehouse:
            warehouses = self.get_warehouses()
        else:
            warehouses = [None]
        result = defaultdict(lambda: defaultdict(int))

        for warehouse in warehouses:
            usage_prices = usage_type.usageprice_set.filter(
                start__lte=end,
                end__gte=start,
                type=usage_type,
            )
            if warehouse:
                usage_prices = usage_prices.filter(warehouse=warehouse)
            usage_prices = usage_prices.order_by('start')

            if usage_type.by_warehouse:
                count_symbol = '{0}_count_{1}'.format(usage_type.id, warehouse.id)
                cost_symbol = '{0}_cost_{1}'.format(usage_type.id, warehouse.id)
                total_cost_symbol = '{0}_total_cost'.format(usage_type.id)
            else:
                count_symbol = '{0}_count'.format(usage_type.id)
                cost_symbol = '{0}_cost'.format(usage_type.id)

            for usage_price in usage_prices:
                if forecast:
                    price = usage_price.forecast_price
                else:
                    price = usage_price.price
                if usage_type.by_cost:
                    price = self._get_price_from_cost(
                        usage_price,
                        forecast,
                        warehouse
                    )

                up_start = max(start, usage_price.start)
                up_end = min(end, usage_price.end)

                usages_per_venture = self._get_usages_in_period_per_venture(
                    up_start,
                    up_end,
                    usage_type,
                    warehouse,
                    ventures,
                )
                for v in usages_per_venture:
                    venture = v['pricing_venture']
                    result[venture][count_symbol] = v['usage']
                    cost = D(v['usage']) * price
                    result[venture][cost_symbol] = cost
                    if usage_type.by_warehouse:
                        result[venture][total_cost_symbol] += cost

        return result

    def usages(self, start, end, ventures, usage_type, forecast=False, **kwargs):
        logger.debug("Get {0} usage".format(usage_type.name))
        return self._get_usages_per_warehouse(
            start=start,
            end=end,
            ventures=ventures,
            usage_type=usage_type,
            forecast=forecast,
        )

    def schema(self, usage_type, **kwargs):
        logger.debug("Get {0} schema".format(usage_type.name))
        if usage_type.by_warehouse:
            schema = OrderedDict()
            for warehouse in self.get_warehouses():
                schema['{0}_count_{1}'.format(usage_type.id, warehouse.id)] = {
                    'name': _("{0} count ({1})".format(
                        usage_type.name,
                        warehouse.name,
                    )),
                }
                schema['{0}_cost_{1}'.format(usage_type.id, warehouse.id)] = {
                    'name': _("{0} cost ({1})".format(
                        usage_type.name,
                        warehouse.name,
                    )),
                    'currency': True,
                }
            schema['{0}_total_cost'.format(usage_type.id)] = {
                'name': _("{0} total cost".format(usage_type.name)),
                'currency': True,
                'total_cost': True,
            }
        else:
            schema = OrderedDict([
                ('{0}_count'.format(usage_type.id), {
                    'name': _("{0} count".format(usage_type.name)),
                }),
                ('{0}_cost'.format(usage_type.id), {
                    'name': _("{0} cost".format(usage_type.name)),
                    'currency': True,
                    'total_cost': True,
                }),
            ])
        return schema


@register(chain='reports')
class UsagePlugin(UsageBasePlugin):
    pass

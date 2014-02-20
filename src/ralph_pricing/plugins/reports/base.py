# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal as D
from collections import defaultdict

from ralph_pricing.models import DailyUsage
from ralph_pricing.plugins.base import BasePlugin


class AttributeDict(dict):
    """
    Attribute dict. Used to attribute access to dict
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class BaseUsagesPlugin(BasePlugin):
    def get_prices_from_costs(self, start, end, usage_type, warehouse=None):
        """
        Calculate price from cost for each unit of usage

        :param datatime start: Begin of time interval for report
        :param datatime end: End of time interval for report
        :param object usage_type: Usage type for which price will be calculated
        :param object warehouse: Warehouse if price is by warehouse
        :returns list: List with calculated prices
        :rtype list:
        """
        costs = usage_type.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
            warehouse=warehouse,
        ).order_by('start')

        prices = []
        for cost in costs:
            daily_usages = DailyUsage.objects.filter(
                date__gte=cost.start,
                date__lte=cost.end,
                type=usage_type,
            )

            if warehouse:
                daily_usages = daily_usages.filter(warehouse=warehouse)

            total_usage = 0
            for daily_usage in daily_usages:
                total_usage += daily_usage.value
            price = 0
            if total_usage != 0 and cost.cost != 0:
                price = cost.cost / D(total_usage)

            prices.append(
                AttributeDict(end=cost.end, start=cost.start, price=price)
            )

        return prices

    def get_prices(self, start, end, usage_type, warehouse=None):
        """
        Get prices for usage type in given time period

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param object usage_type: Usage type for which price will be calculated
        :param object warehouse: Warehouse if price is by warehouse
        :returns list: List of prices
        :rtype list:
        """
        prices = usage_type.usageprice_set.filter(
            start__lte=end,
            end__gte=start,
        )
        if warehouse:
            prices = prices.filter(warehouse=warehouse)

        return prices.order_by('start')

    def generate_prices_list(self, start, end, prices):
        """
        Create a prices list as dict where key is date and value is price

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param list prices: List of pirces with time periods
        :returns dict: Dict with price for each day
        :rtype dict:
        """
        prices_list = {}
        for price in prices:
            delta = price.end - price.start
            for i in xrange(delta.days + 1):
                date = price.start + timedelta(days=i)
                if date >= start and date <= end:
                    prices_list[str(date)] = price.price

        if not prices_list:
            return 'No Price'

        if (end-start).days + 1 != len(prices_list):
            return 'Incomplete Price'

        return prices_list

    def prepare_data(self, daily_usages, prices_list):
        """
        Create a finally dict where venture is a key but value is dict contains
        informations like value and cost. Cost is calculated based on value of
        usage and then is count to one value. If price for give data is a string,
        then string is assigned to the field instead of calculating price

        :param dict daily_usages: Daily usages for each venture from all days
        :param dict prices_list: prices list for each day
        :returns dict: count and price together and venture id as a key
        :rtype dict:
        """
        count_and_price = defaultdict(lambda: defaultdict(int))
        for daily_usage in daily_usages:
            count_and_price[daily_usage['pricing_venture']]['value'] +=\
                daily_usage['value']
            if isinstance(prices_list, dict):
                count_and_price[daily_usage['pricing_venture']]['cost'] +=\
                    D(daily_usage['value']) * prices_list.get(
                        str(daily_usage['date'].date()))
            else:
                count_and_price[daily_usage['pricing_venture']]['cost'] =\
                    prices_list

        return count_and_price

    def get_daily_usages(
        self,
        start,
        end,
        ventures,
        usage_type,
        warehouse=None,
    ):
        """
        Get all usages for given usage types and ventures

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param object usage_type: Usage type for which price will be calculated
        :param object warehouse: Warehouse if price is by warehouse
        :returns list: query with selected daily usages
        :rtype list:
        """
        daily_usages = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
            type=usage_type,
        ).values(
            'pricing_venture',
            'value',
            'date',
        )
        if warehouse:
            daily_usages = daily_usages.filter(warehouse=warehouse)

        return daily_usages

    def get_usages_and_costs(
        self,
        start,
        end,
        ventures,
        usage_type,
        warehouse=None,
    ):
        """
        Get usages and costs based on standard algorithm. The sandard algorithm
        get all usages and price for them (or calculate from cost). Then value
        from each day is multiply by price and everything is summed together for
        each venture. At the end everything is joined to one dict where key is
        venture id and value is dict with cost and price

        :param datatime start: Start of time interval for report
        :param datatime end: End of time interval for report
        :param object usage_type: Usage type for which price will be calculated
        :param object warehouse: Warehouse if price is by warehouse
        :returns dict: usage and cost for each venture
        :rtype dict:
        """
        daily_usages = self.get_daily_usages(
            start,
            end,
            ventures,
            usage_type,
            warehouse,
        )

        if usage_type.by_cost:
            prices = self.get_prices_from_costs(start, end, usage_type, warehouse)
        else:
            prices = self.get_prices(start, end, usage_type, warehouse)
        prices_list = self.generate_prices_list(start, end, prices)

        return self.prepare_data(daily_usages, prices_list)

import logging
from decimal import Decimal as D
from datetime import timedelta
from collections import defaultdict

from ralph_pricing.models import DailyUsage


class AttributeDict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def get_prices_from_costs(start, end, usage_type, warehouse):
    costs = usage_type.usageprice_set.filter(
        start__lte=end,
        end__gte=start,
        warehouse=warehouse,
    )

    prices = []
    for cost in costs:
        daily_usages = DailyUsage.objects.filter(
            date__gte=cost.start,
            date__lte=cost.end,
            type=usage_type,
            warehouse=warehouse,
        )

        total_usage = 0
        for daily_usage in daily_usages:
            total_usage += daily_usage.value
        price = 0
        if total_usage != 0 and cost.cost != 0:
            price = cost.cost / D(total_usage) / (
                (cost.end - cost.start).days + 1)

        prices.append(
            AttributeDict(
                end = cost.end,
                start = cost.start,
                price = price,
            )
        )

    return prices


def get_prices(start, end, usage_type, warehouse=None):
    prices = usage_type.usageprice_set.filter(
        start__lte=end,
        end__gte=start,
    )
    if warehouse:
        prices = prices.filter(warehouse=warehouse)

    return prices


def generate_prices_list(start, end, prices):
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


def prepare_data(daily_usages, prices_list):
    count_and_price = defaultdict(lambda : defaultdict(int))
    for daily_usage in daily_usages:
        count_and_price[daily_usage['pricing_venture']]['value'] +=\
            daily_usage['value']
        if type(prices_list) == dict:
            count_and_price[daily_usage['pricing_venture']]['cost'] +=\
                D(daily_usage['value']) * prices_list.get(
                    str(daily_usage['date'].date()))
        else:
            count_and_price[daily_usage['pricing_venture']]['cost'] =\
                prices_list

    return count_and_price


def get_daily_usages(
    start,
    end,
    ventures,
    usage_type,
    warehouse=None,
):
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


def get_standard_usages_and_costs(
    start,
    end,
    ventures,
    usage_type,
    warehouse=None,
):
    daily_usages = get_daily_usages(
        start,
        end,
        ventures,
        usage_type,
        warehouse,
    )

    if usage_type.by_cost:
        prices = get_prices_from_costs(start, end, usage_type, warehouse)
    else:
        prices = get_prices(start, end, usage_type, warehouse)
    prices_list = generate_prices_list(start, end, prices)

    return prepare_data(daily_usages, prices_list)

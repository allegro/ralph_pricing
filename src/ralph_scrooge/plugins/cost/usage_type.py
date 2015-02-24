# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from decimal import Decimal as D

from ralph_scrooge.models import UsagePrice
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import (
    BaseCostPlugin,
    NoPriceCostError,
    MultiplePriceCostError,
)
from ralph_scrooge.utils.common import memoize


logger = logging.getLogger(__name__)


class UsageTypeBasePlugin(BaseCostPlugin):
    @memoize(skip_first=True)
    def _get_price_per_unit(
        self,
        date,
        usage_type,
        forecast=False,
        warehouse=None,
        excluded_services=None,
        excluded_services_environments=None,
    ):
        """
        Returns price for single unit of usage for date.
        Check if usage type cost / price is defined for specified date

        :param datetime.date date: date to get price per unit
        :param UsageType usage_type: usage type
        :param Warehouse warehouse: warehouse to check
        :returns tuple: total usage for usage price period, price per unit
        """
        usage_price = usage_type.usageprice_set.filter(
            end__gte=date,
            start__lte=date,
        )
        if usage_type.by_warehouse and warehouse:
            usage_price = usage_price.filter(warehouse=warehouse)
        try:
            usage_price = usage_price.get()
        except UsagePrice.DoesNotExist:
            raise NoPriceCostError()
        except UsagePrice.MultipleObjectsReturned:
            raise MultiplePriceCostError()

        if usage_type.by_cost:
            price = self._get_price_from_cost(
                usage_price,
                forecast=forecast,
                warehouse=warehouse,
                excluded_services=excluded_services,
                excluded_services_environments=excluded_services_environments,
            )
        else:
            if forecast:
                price = usage_price.forecast_price
            else:
                price = usage_price.price

        return price

    def _get_costs_per_warehouse(
        self,
        usage_type,
        date,
        forecast,
    ):
        """
        Returns information about usage (of usage type) count and cost
        per service for date using forecast or real price or cost.
        """
        excluded_services_envs = usage_type.excluded_services_environments
        if usage_type.by_warehouse:
            warehouses = self.get_warehouses()
        else:
            warehouses = [None]
        result = defaultdict(list)

        for warehouse in warehouses:
            price_per_unit = self._get_price_per_unit(
                date,
                usage_type,
                forecast=forecast,
                warehouse=warehouse,
                excluded_services_environments=excluded_services_envs,
            )
            usages = self._get_usages_per_pricing_object(
                date=date,
                usage_type=usage_type,
                warehouse=warehouse,
                excluded_services_environments=excluded_services_envs,
            )
            for v in usages:
                service_environment = v.service_environment_id
                pricing_object_cost = {
                    'cost': D(v.value) * price_per_unit,
                    'value': v.value,
                    'pricing_object_id': (
                        v.daily_pricing_object.pricing_object_id
                    ),
                    'type_id': usage_type.id,
                }
                if warehouse:
                    pricing_object_cost['warehouse'] = warehouse
                result[service_environment].append(pricing_object_cost)

        return result

    @memoize(skip_first=True)
    def _costs(
        self,
        date,
        usage_type,
        forecast=False,
        **kwargs
    ):
        """
        Returns costs for specified services envrionments (for one day - date).

        :rtype: dict of dicts, ex:
        {
            service_environment1.id : [
                {
                    'cost': Decimal('11.11'),
                    'warehouse': warehouse1,
                    'pricing_object_id': pricing_object1.id,
                },
                {
                    'cost': Decimal('155.11'),
                    'warehouse': warehouse2,
                    'pricing_object_id': pricing_object2.id,
                },
                {
                    'cost': Decimal('15.11'),
                    'warehouse': warehouse2,
                    'pricing_object_id': pricing_object3.id,
                },
            ],
            service_environment2.id: [
                ...
            ],
            ...
        }
        """
        logger.info("Calculating usage type costs: {0}".format(
            usage_type.name,
        ))
        return self._get_costs_per_warehouse(
            date=date,
            usage_type=usage_type,
            forecast=forecast,
        )


@register(chain='scrooge_costs')
class UsageTypePlugin(UsageTypeBasePlugin):
    """
    Base Usage Plugin as ralph plugin. Splitting it into two classes gives
    ability to inherit from UsageBasePlugin.
    """
    pass

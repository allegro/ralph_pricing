# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
from decimal import Decimal as D

from django.db.models import Sum
from ralph_scrooge.utils.common import memoize

from ralph_scrooge.models import DailyUsage
from ralph_scrooge.plugins.base import BasePlugin

logger = logging.getLogger(__name__)


class NoPriceCostError(Exception):
    """
    Raised when price is not defined for specified date.
    """
    pass


class MultiplePriceCostError(Exception):
    """
    Raised when multiple prices are defined for specified date.
    """


class BaseCostPlugin(BasePlugin):
    """
    Base cost plugin

    Every plugin which inherit from BaseCostPlugin should implement 1
    methods - costs.

    This class provides base methods for costs calculation, such as generating
    usages (for given date) per service environment, pricing object etc.
    """
    def run(self, type='costs', *args, **kwargs):
        # find method with name the same as type param
        if hasattr(self, type):
            func = getattr(self, type)
            if hasattr(func, '__call__'):
                return func(*args, **kwargs)
        raise AttributeError()

    def costs(self, service_environments=None, *args, **kwargs):
        """
        Return information about costs of some type (ex. team, service)
        filtered by passed service environments (if passed - otherwise it's
        simple proxt to _costs method, which should be cached).
        """
        costs = self._costs(*args, **kwargs)
        # filter by service environments if specified
        if service_environments:
            se_ids = set([se.id for se in service_environments])
            costs = {k: v for (k, v) in costs.iteritems() if k in se_ids}
        return costs

    @abc.abstractmethod
    def _costs(self, *args, **kwargs):
        """
        Should returns information about costs of some type (ex. team, service)
        per service environment in format accepted by collector (dictionary,
        with service_environment id as a key and value is list dictonaries with
        costs definition. Example of single cost:
        {
            'cost': Decimal('100.12'),
            'value': 300.12,  # usage of resource/type
            'pricing_object_id': 1234  # optional, but it's preffered to return
                here dummy pricing object id if concrete is not known
            'type_id': 11,
        }
        """

    def total_cost(self, *args, **kwargs):
        """
        By default total cost is just sum of all costs from `costs` method.
        """
        costs = self.costs(*args, **kwargs)
        return sum([sum([s['cost'] for s in c]) for c in costs.values()])

    @memoize(skip_first=True)
    def _get_price_from_cost(
        self,
        usage_price,
        forecast,
        warehouse=None,
        service_environments=None,
        excluded_services=None,
        excluded_services_environments=None
    ):
        """
        Calculate price for single unit of usage type in period of time defined
        by daterange of usage_price.

        Price can be calculated overall or for single warehouse.
        """
        total_usage = self._get_total_usage(
            usage_type=usage_price.type,
            start=usage_price.start,
            end=usage_price.end,
            warehouse=warehouse,
            service_environments=service_environments,
            excluded_services=excluded_services,
            excluded_services_environments=excluded_services_environments,
        )
        cost = usage_price.forecast_cost if forecast else usage_price.cost
        price = 0
        if total_usage and cost:
            price = cost / D(total_usage)
        return D(price)

    def _get_daily_usages_in_period(
        self,
        usage_type,
        date=None,
        start=None,
        end=None,
        warehouse=None,
        service_environments=None,
        excluded_services=None,
        excluded_services_environments=None
    ):
        """
        Filter daily usages based on passed params
        """
        daily_usages = DailyUsage.objects.filter(
            type=usage_type,
        )
        if start and end:
            daily_usages = daily_usages.filter(date__gte=start, date__lte=end)
        elif date:
            daily_usages = daily_usages.filter(date=date)

        if warehouse:
            daily_usages = daily_usages.filter(warehouse=warehouse)
        if service_environments is not None:
            daily_usages = daily_usages.filter(
                service_environment__in=service_environments
            )
        if excluded_services:
            daily_usages = daily_usages.exclude(
                service_environment__service__in=excluded_services
            )
        if excluded_services_environments:
            daily_usages = daily_usages.exclude(
                service_environment__in=excluded_services_environments
            )
        return daily_usages.select_related('daily_pricing_object')

    @memoize(skip_first=True)
    def _get_total_usage(self, *args, **kwargs):
        """
        Calculates total usage of usage type in period of time (between start
        and end). Total usage can be calculated overall, for single warehouse,
        for selected services or for services in warehouse.

        :rtype: float
        """
        daily_usages = self._get_daily_usages_in_period(*args, **kwargs)
        return daily_usages.aggregate(
            total=Sum('value')
        ).get('total') or 0

    def _get_usages_per_service_environment(self, *args, **kwargs):
        """
        Method similar to `_get_total_usage_in_period`, but instead of
        one-number result, it returns total cost per service in period of time
        (between start and end). Total usage can be calculated overall, for
        single warehouse, for selected services or for services in warehouse.

        :rtype: list
        """
        daily_usages = self._get_daily_usages_in_period(*args, **kwargs)
        return list(daily_usages.values('service_environment').annotate(
            usage=Sum('value'),
        ).order_by('service_environment'))

    def _get_usages_per_service(self, *args, **kwargs):
        """
        Method similar to `_get_total_usage_in_period`, but instead of
        one-number result, it returns total cost per service in period of time
        (between start and end). Total usage can be calculated overall, for
        single warehouse, for selected services or for services in warehouse.

        :rtype: list
        """
        daily_usages = self._get_daily_usages_in_period(*args, **kwargs)
        return list(
            daily_usages.values('service_environment__service').annotate(
                usage=Sum('value'),
            ).order_by('service_environment__service')
        )

    def _get_usages_per_pricing_object(self, *args, **kwargs):
        """
        Works almost exactly as `_get_usages_in_period_per_service`, but
        instead of returning data grouped by service, it returns usages
        aggregated by single pricing_object.

        :rtype: list
        """
        daily_usages = self._get_daily_usages_in_period(*args, **kwargs)
        return daily_usages

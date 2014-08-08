# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
from collections import defaultdict
from decimal import Decimal as D

from django.db.models import Sum
from lck.cache import memoize

from ralph_scrooge.models import DailyUsage
from ralph_scrooge.models import UsageType
from ralph_scrooge.plugins.base import BasePlugin

logger = logging.getLogger(__name__)


class BaseReportPlugin(BasePlugin):
    """
    Base report plugin

    Every plugin which inherit from BaseReportPlugin should implement 3
    methods: usages, schema and total_cost.

    Usages and schema methods are connected - schema defines output format of
    usages method. Usages method should return information about usages (one
    or more types - depending on plugins needs) per every service.
    """
    distribute_count_key_tmpl = 'ut_{0}_count'
    distribute_cost_key_tmpl = 'ut_{0}_cost'

    def run(self, type='costs', *args, **kwargs):
        # find method with name the same as type param
        if hasattr(self, type):
            func = getattr(self, type)
            if hasattr(func, '__call__'):
                return func(*args, **kwargs)
        raise AttributeError()

    @abc.abstractmethod
    def costs(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def schema(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def total_cost(self, *args, **kwargs):
        pass

    def _distribute_costs(
        self,
        start,
        end,
        services,
        cost,
        percentage,
    ):
        """
        Distributes some cost between all services proportionally to usages of
        pricing service resources (taken from percentage).
        """
        # first level: service
        # second level: usage type key (count or cost)
        result = defaultdict(lambda: defaultdict(int))
        usage_types = {}  # usage types cache

        for usage_type_id, percent in percentage.items():
            usage_type = usage_types.setdefault(
                usage_type_id,
                UsageType.objects.get(id=usage_type_id)
            )
            usages_per_service = self._get_usages_per_service_environment(
                start,
                end,
                usage_type,
                services=services,
            )
            total_usage = self._get_total_usage_in_period(
                start,
                end,
                usage_type,
            )
            cost_part = D(percent) * cost / D(100)

            count_key = self.distribute_count_key_tmpl.format(usage_type_id)
            cost_key = self.distribute_cost_key_tmpl.format(usage_type_id)

            for service_usage in usages_per_service:
                service_environment = service_usage['service_environment']
                usage = service_usage['usage']
                result[service_environment][count_key] = usage
                service_cost = D(usage) / D(total_usage) * cost_part
                result[service_environment][cost_key] = service_cost
        return result

    @memoize(skip_first=True)
    def _get_price_from_cost(
        self,
        usage_price,
        forecast,
        warehouse=None,
        services=None,
        excluded_services=None,
    ):
        """
        Calculate price for single unit of usage type in period of time defined
        by daterange of usage_price.

        Price can be calculated overall or for single warehouse.
        """
        total_usage = self._get_total_usage_in_period(
            usage_price.start,
            usage_price.end,
            usage_price.type,
            warehouse,
            services,
            excluded_services,
        )
        cost = usage_price.forecast_cost if forecast else usage_price.cost
        price = 0
        if total_usage and cost:
            price = cost / D(total_usage)
        return D(price)

    @memoize(skip_first=True)
    def _get_daily_usages_in_period(
        self,
        start,
        end,
        usage_type,
        warehouse=None,
        services=None,
        excluded_services=None,
    ):
        """
        Filter daily usages based on passed params
        """
        daily_usages = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            type=usage_type,
        )
        if warehouse:
            daily_usages = daily_usages.filter(warehouse=warehouse)
        if services:
            daily_usages = daily_usages.filter(
                service_environment__service__in=services
            )
        if excluded_services:
            daily_usages = daily_usages.exclude(
                service_environment__service__in=excluded_services
            )
        return daily_usages

    @memoize(skip_first=True)
    def _get_total_usage_in_period(self, *args, **kwargs):
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

    @memoize(skip_first=True)
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

    @memoize(skip_first=True)
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

    # TODO: rename
    @memoize(skip_first=True)
    def _get_usages_in_period_per_device(
        self,
        start,
        end,
        usage_type,
        services=None,
        warehouse=None,
        excluded_services=None,
    ):
        """
        Works almost exactly as `_get_usages_in_period_per_service`, but
        instead of returning data grouped by service, it returns usages
        aggregated by single device.

        :rtype: list
        """
        # TODO: change to usage per pricing object (pass pricing object type)
        # TODO: use self._get_daily_usages_in_period
        daily_usages = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            type=usage_type,
        )
        if services:
            daily_usages = daily_usages.filter(
                service_environment__service__in=services
            )
        if excluded_services:
            daily_usages = daily_usages.exclude(
                service_environment__service__in=excluded_services
            )
        if warehouse:
            daily_usages = daily_usages.filter(warehouse=warehouse)
        return list(daily_usages.values(
            'daily_pricing_object__pricing_object'
        ).annotate(usage=Sum('value')).order_by(
            'daily_pricing_object__pricing_object'
        ))

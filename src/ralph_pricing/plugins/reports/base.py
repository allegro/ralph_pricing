# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import logging
from decimal import Decimal as D

from django.db.models import Sum
from lck.cache import memoize

from ralph_pricing.models import DailyUsage
from ralph_pricing.plugins.base import BasePlugin

logger = logging.getLogger(__name__)


class AttributeDict(dict):
    """
    Attribute dict. Used to attribute access to dict
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class BaseReportPlugin(BasePlugin):
    """
    Base report plugin

    Every plugin which inherit from BaseReportPlugin should implement 3
    methods: usages, schema and total_cost.

    Usages and schema methods are connected - schema defines output format of
    usages method. Usages method should return informations about usages (one
    or more types - depending on plugins needs) per every venture.
    """
    def run(self, type='usages', *args, **kwargs):
        # find method with name the same as type param
        if hasattr(self, type):
            func = getattr(self, type)
            if hasattr(func, '__call__'):
                return func(*args, **kwargs)
        raise AttributeError()

    @abc.abstractmethod
    def usages(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def schema(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def total_cost(self, *args, **kwargs):
        pass

    @memoize(skip_first=True)
    def _get_price_from_cost(
        self,
        usage_price,
        forecast,
        warehouse=None,
        ventures=None,
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
            ventures,
        )
        cost = usage_price.forecast_cost if forecast else usage_price.cost
        if total_usage == 0:
            price = 0
        else:
            price = cost / D(total_usage)
        return D(price)

    @memoize(skip_first=True)
    def _get_total_usage_in_period(
        self,
        start,
        end,
        usage_type,
        warehouse=None,
        ventures=None,
    ):
        """
        Calculates total usage of usage type in period of time (between start
        and end). Total usage can be calculated overall, for single warehouse,
        for selected ventures or for ventures in warehouse.

        :rtype: float
        """
        daily_usages = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            type=usage_type,
        )
        if warehouse:
                daily_usages = daily_usages.filter(warehouse=warehouse)
        if ventures:
            daily_usages = daily_usages.filter(pricing_venture__in=ventures)

        total_usage = daily_usages.aggregate(
            total=Sum('value')
        ).get('total') or 0
        return total_usage

    @memoize(skip_first=True)
    def _get_usages_in_period_per_venture(
        self,
        start,
        end,
        usage_type,
        warehouse=None,
        ventures=None,
    ):
        """
        Method similar to `_get_total_usage_in_period`, but instead of
        one-number result, it returns total cost per venture in period of time
        (between start and end). Total usage can be calculated overall, for
        single warehouse, for selected ventures or for ventures in warehouse.

        :rtype: list
        """
        daily_usages = DailyUsage.objects.filter(
            date__gte=start,
            date__lte=end,
            type=usage_type,
        )
        if warehouse:
                daily_usages = daily_usages.filter(warehouse=warehouse)
        if ventures:
            daily_usages = daily_usages.filter(pricing_venture__in=ventures)
        result = daily_usages.values('pricing_venture').annotate(
            usage=Sum('value'),
        ).order_by('pricing_venture')
        return list(result)

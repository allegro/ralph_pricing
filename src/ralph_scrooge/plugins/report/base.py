# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge.models import DailyCost
from ralph_scrooge.plugins.base import BasePlugin


logger = logging.getLogger(__name__)


class BaseReportPlugin(BasePlugin):
    """
    Base report plugin

    Every plugin which inherit from BaseReportPlugin should implement 3
    methods: usages, schema and total_cost.

    Usages and schema methods are connected - schema defines output format of
    usages method. Usages method should return information about usages (one
    or more types - depending on plugins needs) per every venture.
    """

    base_usage_count_symbol = None
    base_usage_cost_symbol = None

    def run(self, type='costs', *args, **kwargs):
        # find method with name the same as type param
        if hasattr(self, type):
            func = getattr(self, type)
            if hasattr(func, '__call__'):
                return func(*args, **kwargs)
        raise AttributeError()

    def costs(
        self,
        start,
        end,
        base_usage,
        service_environments=None,
        forecast=False,
        *args,
        **kwargs
    ):
        """
        Return cost for given service. Format of
        returned data looks like:

        usages = {
            'service_id': [{
                'cost': cost,
            }],
            ...
        }

        :returns dict: cost per service
        """
        logger.debug("Get {} usages".format(base_usage))

        daily_costs_query = DailyCost.objects.filter(
            date__gte=start,
            date__lte=end,
            type=base_usage,
            forecast=forecast,
        )
        if service_environments:
            daily_costs_query = daily_costs_query.filter(
                service_environment__in=service_environments,
            )
        daily_costs = daily_costs_query.values(
            'service_environment_id'
        ).annotate(
            total_cost=Sum('cost'),
            total_value=Sum('value'),
        )

        usages = defaultdict(lambda: defaultdict(list))
        for daily_cost in daily_costs:
            if self.base_usage_cost_symbol:
                usages[daily_cost['service_environment_id']][
                    self.base_usage_cost_symbol.format(base_usage.id)
                ] = daily_cost['total_cost']
            if self.base_usage_count_symbol:
                usages[daily_cost['service_environment_id']][
                    self.base_usage_count_symbol.format(base_usage.id)
                ] = daily_cost['total_value']
        return usages

    def schema(self, base_usage, *args, **kwargs):
        schema = OrderedDict()
        if self.base_usage_cost_symbol:
            schema[self.base_usage_cost_symbol.format(base_usage.id)] = {
                'name': _("{0} cost".format(base_usage.name)),
                'currency': True,
                'total_cost': True,
            }
        if self.base_usage_count_symbol:
            schema[self.base_usage_count_symbol.format(base_usage.id)] = {
                'name': _("{0} count".format(base_usage.name)),
                'rounding': base_usage.rounding,
                'divide_by': base_usage.divide_by,
            }
        return schema

    def usages(self, *args, **kwargs):
        raise NotImplementedError()

    def usages_schema(self, *args, **kwargs):
        raise NotImplementedError()

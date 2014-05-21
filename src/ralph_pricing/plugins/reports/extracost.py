# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict
from decimal import Decimal as D

from django.db.models import Sum

from ralph_pricing.models import ExtraCostType, DailyExtraCost
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.base import BaseReportPlugin


logger = logging.getLogger(__name__)


@register(chain='reports')
class ExtraCostPlugin(BaseReportPlugin):
    """
    Extra cost plugin, generate schema, total cost and cost from daily extra
    cost model.
    """
    key_name = 'extra_cost_{}'

    def get_extra_costs(self, start, end, ventures):
        """
        Get daily extra costs for given dates and ventures

        :param datatime start: Begin of time interval
        :param datatime end: End of time interval
        :param list ventures: List of ventures
        :returns dict: query with selected extra costs for give ventures
        :rtype dict:
        """
        return DailyExtraCost.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
        )

    def costs(self, start, end, ventures, *args, **kwargs):
        """
        Return usages and costs for given ventures. Format of
        returned data looks like:

        usages = {
            'venture_id': {
                'field_name': value,
                ...
            },
            ...
        }

        :returns dict: usages and costs
        """
        logger.debug("Get extra costs usages")
        extra_costs = self.get_extra_costs(
            start,
            end,
            ventures,
        ).values('pricing_venture', 'type').annotate(
            total_cost=Sum('value')
        )

        usages = defaultdict(lambda: defaultdict(int))
        for extra_cost in extra_costs:
            usages[extra_cost['pricing_venture']][
                self.key_name.format(extra_cost['type'])
            ] += (
                extra_cost['total_cost']
            )
            usages[extra_cost['pricing_venture']]['extra_costs_total'] += (
                extra_cost['total_cost']
            )

        return usages

    def schema(self, *args, **kwargs):
        """
        Build schema for this usage. Format of schema looks like:

        schema = {
            'field_name': {
                'name': 'Verbous name',
                'next_option': value,
                ...
            },
            ...
        }

        :returns dict: schema for usage
        :rtype dict:
        """
        logger.debug("Get extra costs schema")
        schema = OrderedDict()
        for extra_cost_type in ExtraCostType.objects.all():
            schema[self.key_name.format(extra_cost_type.id)] = {
                'name': extra_cost_type.name,
                'currency': True,
            }
        schema['extra_costs_total'] = {
            'name': 'Extra Costs Total',
            'currency': True,
            'total_cost': True,
        }
        return schema

    def total_cost(self, start, end, ventures, **kwargs):
        """
        Calculate total cost for given ventures in given time period.

        :param datatime start: Begin of time interval for deprecation
        :param datatime end: End of time interval for deprecation
        :param list ventures: List of ventures
        :returns dict: total cost for given time period and ventures
        :rtype dict:
        """
        return D(self.get_extra_costs(start, end, ventures).aggregate(
            total_cost=Sum('value')
        )['total_cost'] or 0)

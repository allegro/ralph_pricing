# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict
from decimal import Decimal as D

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ralph_pricing.models import ExtraCostType, DailyExtraCost
from ralph_pricing.plugins.base import register
from ralph_pricing.plugins.reports.base import BaseReportPlugin


logger = logging.getLogger(__name__)


@register(chain='reports')
class ExtraCostPlugin(BaseReportPlugin):
    def get_extra_costs(self, start, end, ventures):
        daily_extra_costs = DailyExtraCost.objects.filter(
            date__gte=start,
            date__lte=end,
            pricing_venture__in=ventures,
        )
        return daily_extra_costs

    def costs(self, *args, **kwargs):
        """
        """
        logger.debug("Get extra costs usages")
        extra_costs = self.get_extra_costs(
            kwargs['start'],
            kwargs['end'],
            kwargs['ventures'],
        )

        usages = defaultdict(lambda : defaultdict(int))
        for extra_cost in extra_costs:
            venture_id = extra_cost.pricing_venture.id
            usages[venture_id][extra_cost.type.name] += extra_cost.value
            usages[venture_id]['extra_costs_total_cost'] += extra_cost.value
        return usages

    def schema(self, *args, **kwargs):
        """
        """
        logger.debug("Get extra costs schema")
        schema = OrderedDict()
        for extra_cost_type in ExtraCostType.objects.all():
            schema[extra_cost_type.name] = {
                'name': extra_cost_type.name,
                'currency': True,
            }
        schema['extra_costs_total_cost'] = {
            'name': 'Extra Costs Total',
            'currency': True,
            'total_cost': True,
        }
        return schema

    def total_cost(self, start, end, ventures, **kwargs):
        extra_costs_query = self.get_extra_costs(
            start, end, ventures).aggregate(
                total_cost=Sum('value')
        )
        return D(extra_costs_query['total_cost'] or 0)

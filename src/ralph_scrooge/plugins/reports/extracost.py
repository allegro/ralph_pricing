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

from ralph_scrooge.models import ExtraCost, ExtraCostType, DailyCost
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.reports.base import BaseReportPlugin
from ralph_scrooge.plugins.cost.base import (
    BaseCostPlugin,
)

logger = logging.getLogger(__name__)


@register(chain='scrooge_reports')
class ExtraCostPlugin(BaseReportPlugin):
    """
    Extra cost plugin, total cost and cost from daily extra
    cost model.
    """

    extra_cost_count_symbol = '{0}_extracost_count'
    extra_cost_cost_symbol = '{0}_extracost_cost'

    def costs(self, start, end, service_environments, extra_cost_type, *args, **kwargs):
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
        logger.debug("Get extra costs usages")

        daily_costs = DailyCost.objects.filter(
            date__gte=start,
            date__lte=end,
            service_environment__in=service_environments,
            type=extra_cost_type,
        ).values(
            'service_environment__id'
        ).annotate(
            total_cost=Sum('cost'),
            total_value=Sum('value'),
        )

        usages = defaultdict(lambda: defaultdict(list))
        for daily_cost in daily_costs:
            usages[daily_cost['service_environment__id']][
                self.extra_cost_cost_symbol.format(extra_cost_type.name)
            ] = daily_cost['total_cost']

        return usages

    def schema(self, extra_cost_type, *args, **kwargs):
        schema = OrderedDict()
        schema[self.extra_cost_cost_symbol.format(extra_cost_type.name)] = {
            'name': _("{0} cost".format(extra_cost_type.name)),
            'currency': True,
        }
        return schema

    def total_cost(self, *args, **kwargs):
        return D(0)

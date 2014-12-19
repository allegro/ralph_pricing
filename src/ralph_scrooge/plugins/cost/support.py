# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

from ralph_scrooge.models import DailyPricingObject, ExtraCostType, SupportCost
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import BaseCostPlugin

logger = logging.getLogger(__name__)


@register(chain='scrooge_costs')
class SupportPlugin(BaseCostPlugin):
    """
    Support cost plugin, total cost and cost from daily extra
    cost model.
    """

    def costs(
        self,
        date,
        service_environments,
        forecast=False,
        *args,
        **kwargs
    ):
        """
        Return extra costs for date per services environments.

        :returns dict: dict of list of dicts

        Example result:
        {
            service_environment1.id : [
                {'type': extra_cost1.id, cost: 100},
                {'type': extra_cost1.id, cost: 200},
            ],
            service_environment2.id: [
                {'type': extra_cost1.id, cost: 300},
            ],
            ...
        }
        """
        logger.debug("Get support costs")
        support_type = ExtraCostType.objects.get(pk=2)  # from fixture
        daily_po = dict(DailyPricingObject.objects.filter(
            service_environment__in=service_environments,
            date=date
        ).values_list('pricing_object_id', 'service_environment_id'))
        supports = SupportCost.objects.filter(
            end__gte=date,
            start__lte=date,
            pricing_object__in=daily_po.keys(),
        )

        usages = defaultdict(list)
        for support in supports:
            cost = support.forecast_cost if forecast else support.cost
            usages[daily_po[support.pricing_object_id]].append({
                'cost': (cost / (
                    (support.end - support.start).days + 1)
                ),
                'type': support_type,
            })
        return usages

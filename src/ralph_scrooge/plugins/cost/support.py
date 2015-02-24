# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict, namedtuple

from ralph_scrooge.models import ExtraCostType, SupportCost
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import BaseCostPlugin
from ralph_scrooge.utils.common import memoize

logger = logging.getLogger(__name__)


SupportRecord = namedtuple(
    'SupportRecord',
    [
        'service_environment_id',
        'pricing_object_id',
        'cost',
        'forecast_cost',
        'start',
        'end',
    ]
)


@register(chain='scrooge_costs')
class SupportPlugin(BaseCostPlugin):
    """
    Support cost plugin, total cost and cost from daily extra
    cost model.
    """

    @memoize(skip_first=True)
    def _costs(
        self,
        date,
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
        logger.info("Calculating supports costs")
        support_type = ExtraCostType.objects.get(pk=2)  # from fixture
        usages = defaultdict(list)
        supports = SupportCost.objects.filter(
            end__gte=date,
            start__lte=date,
            pricing_object__daily_pricing_objects__date=date,
        ).values_list(
            'pricing_object__daily_pricing_objects__service_environment_id',
            'pricing_object_id',
            'cost',
            'forecast_cost',
            'start',
            'end',
        )
        for support in map(SupportRecord._make, list(supports)):
            cost = support.forecast_cost if forecast else support.cost
            usages[support.service_environment_id].append({
                'cost': (cost / (
                    (support.end - support.start).days + 1)
                ),
                'type': support_type,
                'pricing_object_id': support.pricing_object_id
            })
        return usages

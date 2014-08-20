# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

from ralph_scrooge.models import ExtraCost
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import (
    BaseCostPlugin,
)

logger = logging.getLogger(__name__)


@register(chain='scrooge_costs')
class ExtraCostPlugin(BaseCostPlugin):
    """
    Extra cost plugin, total cost and cost from daily extra
    cost model.
    """

    def costs(self, date, service_environments, extra_cost_type, *args, **kwargs):
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

        extra_costs = ExtraCost.objects.filter(
            end__gte=date,
            start__lte=date,
            service_environment__in=service_environments,
            extra_cost_type=extra_cost_type,
        )

        usages = defaultdict(list)
        for extra_cost in extra_costs:
            usages[extra_cost.service_environment.id].append(
                {
                    'cost': (extra_cost.cost /
                             ((extra_cost.end - extra_cost.start).days + 1)
                             ),
                    'type': extra_cost_type,
                }
            )
        return usages

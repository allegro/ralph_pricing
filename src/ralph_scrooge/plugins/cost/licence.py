# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

from ralph_scrooge.models import ExtraCostType
from ralph_scrooge.models.extra_cost import LicenceCost
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import BaseCostPlugin
from ralph_scrooge.utils.common import memoize

logger = logging.getLogger(__name__)


@register(chain='scrooge_costs')
class LicencePlugin(BaseCostPlugin):
    """
    Licence cost plugin, total cost and cost from daily extra
    cost model.
    """

    @memoize(skip_first=True)
    def _costs(self, date, forecast=False, *args, **kwargs):
        logger.info("Calculating licences costs")
        # TODO (mbleschke): meaningful value, not 3
        licence_type = ExtraCostType.objects.get(pk=3)  # from fixture
        usages = defaultdict(list)
        licences = LicenceCost.objects.filter(
            end__gte=date,
            start__lte=date,
            pricing_object__daily_pricing_objects__date=date,
        ).values(
            'pricing_object__daily_pricing_objects__service_environment_id',
            'pricing_object_id',
            'cost',
            'forecast_cost',
            'start',
            'end',
        )
        for licence in licences:
            cost = licence['forecast_cost'] if forecast else licence['cost']
            # TODO (mbleschke): this long string to separate variable?
            usages[licence['pricing_object__daily_pricing_objects__service_environment_id']].append({
                'cost': (cost / (
                    (licence['end'] - licence['start']).days + 1)
                ),
                'type': licence_type,
                'pricing_object_id': licence['pricing_object_id']
            })
        return usages

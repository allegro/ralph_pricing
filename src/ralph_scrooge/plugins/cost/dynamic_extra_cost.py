# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph_scrooge.models import DynamicExtraCost
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.base import NoPriceCostError
from ralph_scrooge.plugins.cost.pricing_service import PricingServiceBasePlugin
from ralph_scrooge.utils.common import memoize

logger = logging.getLogger(__name__)


@register(chain='scrooge_costs')
class DynamicExtraCostPlugin(PricingServiceBasePlugin):
    def total_cost(self, for_all_service_environments=False, *args, **kwargs):
        service_costs = self.costs(*args, **kwargs)
        return self._get_total_costs_from_costs(service_costs)

    @memoize(skip_first=True)
    def _costs(
        self,
        dynamic_extra_cost_type,
        date,
        forecast=False,
        **kwargs
    ):
        logger.info("Calculating dynamic extra costs: {0}".format(
            dynamic_extra_cost_type.name,
        ))
        percentage = self._get_percentage(date, dynamic_extra_cost_type)
        costs = self._get_costs(
            date,
            dynamic_extra_cost_type,
            forecast,
        )
        # distribute total cost between every service_environment
        # proportionally to usages
        return self._distribute_costs(
            date,
            dynamic_extra_cost_type,
            costs,
            percentage,
            excluded_services=set(
                dynamic_extra_cost_type.excluded_services.all()
            ),
        )

    def _get_costs(self, date, dynamic_extra_cost_type, forecast, **kwargs):
        try:
            cost = dynamic_extra_cost_type.costs.get(
                end__gte=date,
                start__lte=date,
            )
        except DynamicExtraCost.DoesNotExist:
            raise NoPriceCostError()
        else:

            daily_cost = (
                (cost.forecast_cost if forecast else cost.cost) /
                ((cost.end - cost.start).days + 1)
            )
            return {
                dynamic_extra_cost_type.id: (daily_cost, None)
            }

    def _get_percentage(self, date, dynamic_extra_cost_type):
        """
        Returns list of minimum date ranges that have different percentage
        division in given extra cost type.
        """
        usage_types = dynamic_extra_cost_type.division.all()
        assert abs(sum([s.percent for s in usage_types]) - 100) < 0.01
        return usage_types

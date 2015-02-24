# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from decimal import Decimal as D

from ralph.util import plugin as plugin_runner
from ralph_scrooge.plugins.base import register
from ralph_scrooge.plugins.cost.pricing_service import PricingServiceBasePlugin
from ralph_scrooge.utils.common import memoize

logger = logging.getLogger(__name__)


@register(chain='scrooge_costs')
class PricingServiceFixedPricePlugin(PricingServiceBasePlugin):
    """
    Fixed price service cost is sum of costs of attached service usage types -
    each of this service usage types must has price (and forecast price)
    defined for date, in which costs are generated.
    """
    def total_cost(self, for_all_service_environments=False, *args, **kwargs):
        service_costs = self.costs(*args, **kwargs)
        return self._get_total_costs_from_costs(service_costs)

    @memoize(skip_first=True)
    def _costs(
        self,
        pricing_service,
        date,
        forecast=False,
        **kwargs
    ):
        logger.info(
            (
                "Calculating pricing service costs (using fixed "
                "prices): {0}"
            ).format(
                pricing_service.name,
            )
        )
        result_dict = defaultdict(dict)
        usage_types = pricing_service.usage_types.all()
        for usage_type in usage_types:
            try:
                # results per service environment (list of costs per pricing
                # object as a value)
                costs = plugin_runner.run(
                    'scrooge_costs',
                    usage_type.get_plugin_name(),
                    type='costs',
                    date=date,
                    usage_type=usage_type,
                    forecast=forecast,
                )
                # store costs in hierarchy service environment / pricing object
                # and calculate total cost of cloud per pricing object
                for se, se_costs in costs.items():
                    for cost in se_costs:
                        pricing_object_id = cost.get('pricing_object_id')
                        if pricing_object_id not in result_dict[se]:
                            result_dict[se][pricing_object_id] = {
                                'type_id': pricing_service.id,
                                'pricing_object_id': pricing_object_id,
                                'cost': D(0),
                                '_children': [],
                            }
                        result_dict[se][pricing_object_id]['_children'].append(
                            cost
                        )
                        result_dict[se][pricing_object_id]['cost'] += (
                            cost['cost']
                        )
            except (KeyError, AttributeError):
                logger.warning(
                    'Invalid call for {0} total cost'.format(usage_type.name)
                )
        # return data in format accepted by collector - costs per service
        # environment (without nested dict with pricing object)
        return {k: v.values() for k, v in result_dict.items()}

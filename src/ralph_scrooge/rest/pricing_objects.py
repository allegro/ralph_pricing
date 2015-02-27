#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from ralph_scrooge.rest.components import ComponentsContent

from ralph_scrooge.models import (
    DailyPricingObject,
    PricingObjectType,
)


class PricingObjectsContent(ComponentsContent):
    """A view returning pricing data per pricing object"""

    def get_daily_pricing_objects(
            self, start_date, end_date, service, env=None
    ):
        query = DailyPricingObject.objects.filter(
            service_environment__service__id=service,
            date__gte=start_date,
            date__lte=end_date,
        ).select_related(
            "pricing_object",
            "pricing_object__daily_cost",
        )
        if env:
            query = query.filter(service_environment__environment__id=env)
        return query

    def append_extra(self, value, dpo):
        """Appends some extra data to every row"""
        for daily_cost in dpo.daily_costs:
            pass


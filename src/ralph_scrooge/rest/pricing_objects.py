#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Sum
from django.template.defaultfilters import slugify

from ralph_scrooge.rest.components import ComponentsContent
from ralph_scrooge.models import DailyCost, PricingObject


class PricingObjectsContent(ComponentsContent):
    """A view returning pricing data per pricing object"""

    default_model = 'ralph_scrooge.models.PricingObject'

    def get_daily_pricing_objects(
            self, start_date, end_date, service, env=None
    ):
        query = PricingObject.objects.filter(
            daily_pricing_objects__service_environment__service__id=service,
            daily_pricing_objects__date__gte=start_date,
            daily_pricing_objects__date__lte=end_date,
        )
        if env:
            query = query.filter(
                daily_pricing_objects__service_environment__environment__id=env
            )
        pricing_object_ids = query.values_list('id', flat=True)
        query_daily_cost = DailyCost.objects.filter(
            pricing_object_id__in=pricing_object_ids,
            date__gte=start_date,
            date__lte=end_date,
            service_environment__service__id=service
        )
        if env:
            query_daily_cost = query_daily_cost.filter(
                service_environment__environment__id=env
            )
        query_daily_cost = query_daily_cost.values_list(
            'pricing_object_id', 'type__name'
        ).annotate(Sum('value')).annotate(Sum('cost'))
        daily_costs = {}
        for cost in query_daily_cost:
            daily_costs.setdefault(cost[0], []).append(cost)
        return (query, daily_costs)

    def process_single_type(self, single_type, data):
        """Appends some extra data to every row"""
        query_pricing_object, daily_costs = data
        values = []
        django_fields, headers = self.process_schema(
            settings.PRICING_OBJECTS_TABLE_SCHEMA[single_type.name]
        )
        django_fields.insert(0, 'id')
        for po in query_pricing_object.filter(
            type=single_type,
        ).values_list(*django_fields):
            value = {k: v for k, v in enumerate(po[1:])}
            value['__costs'] = [
                {str(k): v for k, v in enumerate(daily_cost[1:])}
                for daily_cost in daily_costs.get(po[0], [])
            ]
            values.append(value)
        return {
            "name": single_type.name,
            "icon_class": single_type.icon_class,
            "slug": slugify(single_type.name),
            "value": values,
            "schema": headers,
            "cost_schema": {k: v for k, v in enumerate(
                ['Name', 'Value', 'Cost'])
            },
            "color": single_type.color,
        }

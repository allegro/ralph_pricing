#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Sum, Q
from django.template.defaultfilters import slugify
from rest_framework.response import Response

from ralph_scrooge.rest.components import ComponentsContent
from ralph_scrooge.models import (
    DailyCost,
    PricingObject,
    CostDateStatus,
    PricingObjectType,
    PRICING_OBJECT_TYPES,
)


class ObjectCostsContent(ComponentsContent):
    """A view returning pricing data per pricing object"""

    default_model = 'ralph_scrooge.models.PricingObject'

    def get_types(self):
        """
        Returns Pricing Object Types defined in COMPONENTS_TABLE_SCHEMA.
        """
        return PricingObjectType.objects.filter(
            name__in=settings.PRICING_OBJECTS_COSTS_TABLE_SCHEMA.keys()
        )

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
        query = query.distinct()
        query_daily_cost = DailyCost.objects.filter(
            pricing_object_id__in=query.values_list('id', flat=True),
            forecast=False,
            date__in=CostDateStatus.objects.filter(
                accepted=True,
                date__gte=start_date,
                date__lte=end_date
            ).values_list('date', flat=True),
            service_environment__service__id=service
        )
        if env:
            query_daily_cost = query_daily_cost.filter(
                service_environment__environment_id=env
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
            settings.PRICING_OBJECTS_COSTS_TABLE_SCHEMA[single_type.name]
        )
        django_fields.insert(0, 'id')
        for po in query_pricing_object.filter(
            type=single_type,
        ).values_list(*django_fields):
            value = {k: v for k, v in enumerate(po[1:])}
            value['__nested'] = [
                {str(k): v for k, v in enumerate(daily_cost[1:])}
                for daily_cost in daily_costs.get(po[0], [])
            ]
            values.append(value)
        return {
            'name': single_type.name,
            'icon_class': single_type.icon_class,
            'slug': slugify(single_type.name),
            'value': values,
            'schema': headers,
            'nested_schema': {k: v for k, v in enumerate(
                ['Name', 'Value', 'Cost'])
            },
            'color': single_type.color,
        }

    def _get_rest_of_costs(self, start_date, end_date, service, env=None):
        query_daily_cost = DailyCost.objects.filter(
            Q(pricing_object_id=None) |
            Q(pricing_object__type_id__in=[
                PRICING_OBJECT_TYPES.UNKNOWN,
                PRICING_OBJECT_TYPES.DUMMY
            ]),  # Dummy and unknown
            forecast=False,
            date__in=CostDateStatus.objects.filter(
                accepted=True,
                date__gte=start_date,
                date__lte=end_date
            ).values_list('date', flat=True),
            service_environment__service__id=service
        )
        if env:
            query_daily_cost = query_daily_cost.filter(
                service_environment__environment_id=env
            )
        query_daily_cost = query_daily_cost.values_list(
            'type__name'
        ).annotate(Sum('value')).annotate(Sum('cost'))
        daily_costs = []
        for cost in query_daily_cost:
            daily_costs.append({str(k): v for k, v in enumerate(cost)})
        return {
            'name': 'Other',
            'icon_class': 'fa-desktop',
            'slug': 'dummy',
            'value': daily_costs,
            'schema': {'0': 'Name', '1': 'Value', '2': 'Cost'},
            'color': '#ff0000',
        }

    def get(self, request, *args, **kwargs):
        daily_pricing_objects = self.get_daily_pricing_objects(*args, **kwargs)
        results = []
        for single_type in self.get_types():
            results.append(self.process_single_type(
                single_type, daily_pricing_objects
            ))
        results.append(self._get_rest_of_costs(
            *args, **kwargs
        ))
        return Response(results if results else [])

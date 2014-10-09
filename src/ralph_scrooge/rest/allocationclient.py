#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json, calendar
from datetime import date, timedelta

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ralph_scrooge.rest.common import monthToNum
from ralph_scrooge.models import (
    DailyUsage,
    PricingObject,
    DailyPricingObject,
    PricingObjectType,
    ServiceEnvironment,
    ServiceUsageTypes,
    UsageType
)
from ralph.util.views import jsonify

def _get_service_usage_type(service):
    return ServiceUsageTypes.objects.get(
        pricing_service__services__name=service
    )


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def allocation_content(request, *args, **kwargs):
    total = 0
    service_usage_type = _get_service_usage_type(kwargs.get('service'))
    first_day = date(int(kwargs.get('year')), monthToNum(kwargs.get('month')), 1)
    daily_pricing_object = PricingObject.objects.filter(
        service_environment__service__name=kwargs.get('service'),
        type=PricingObjectType.dummy,
    )[0].get_daily_pricing_object(first_day)
    rows = []
    for daily_usage in DailyUsage.objects.filter(
        date=first_day,
        daily_pricing_object=daily_pricing_object,
        type=service_usage_type.usage_type,
    ).select_related(
        "service_environment",
        "service_environment__service",
        "service_environment__environment",
    ):
        rows.append({
            "service": daily_usage.service_environment.service.name,
            "env": daily_usage.service_environment.environment.name,
            "value": daily_usage.value
        })
        total += daily_usage.value
    return [
        {"key": "serviceDivision", "value": {"rows": rows, "total": total}}
    ]


def _clear_daily_usages(
    pricing_objects,
    usage_type,
    first_day,
    days_in_month,
):
    daily_pricing_objects = DailyPricingObject.objects.filter(
        pricing_object__in=pricing_objects,
        date__gte=first_day,
        date__lte=first_day + timedelta(days=days_in_month),
    )
    daily_usage = DailyUsage.objects.filter(
        date__gte=first_day,
        date__lte=first_day + timedelta(days=days_in_month),
        daily_pricing_object__in=daily_pricing_objects,
        type=usage_type,
    ).delete()


@csrf_exempt
@jsonify
@require_http_methods(["POST"])
def allocation_save(request, *args, **kwargs):
    post_data = json.loads(request.raw_post_data)
    if kwargs.get('allocate_type') == 'servicedivision':
        service_usage_type = _get_service_usage_type(post_data['service'])
        pricing_objects = PricingObject.objects.filter(
            service_environment__service__name=post_data['service'],
            type=PricingObjectType.dummy,
        )
        days_in_month = calendar.monthrange(
            post_data['year'],
            monthToNum(post_data['month']),
        )[1]
        first_day = date(post_data['year'], monthToNum(post_data['month']), 1)
        _clear_daily_usages(
            pricing_objects,
            service_usage_type.usage_type,
            first_day,
            days_in_month,
        )
        for row in post_data['rows']:
            service_environment = ServiceEnvironment.objects.get(
                service__name=row['service'],
                environment__name=row['env'],
            )
            for day in xrange(days_in_month):
                iter_date = first_day + timedelta(days=day)
                for pricing_object in pricing_objects:
                    dpo = pricing_object.get_daily_pricing_object(iter_date)
                    daily_usage = DailyUsage.objects.get_or_create(
                        date=iter_date,
                        service_environment=service_environment,
                        daily_pricing_object=dpo,
                        value=row['value'],
                        type=service_usage_type.usage_type,
                    )
    return {'status': True}

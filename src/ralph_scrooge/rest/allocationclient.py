#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.response import Response

import json

from datetime import date, timedelta

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ralph_scrooge.rest.common import get_dates
from ralph_scrooge.models import (
    DailyUsage,
    ExtraCost,
    ExtraCostType,
    PricingObject,
    PricingService,
    DailyPricingObject,
    PRICING_OBJECT_TYPES,
    Service,
    ServiceEnvironment,
    ServiceUsageTypes,
    Team,
    TeamCost,
    TeamServiceEnvironmentPercent,
    UsageType,
)
from ralph.util.views import jsonify


def _get_team_divison(team, start, end):
    total = 0
    rows = []
    for tsep in TeamServiceEnvironmentPercent.objects.filter(
        team_cost__team__id=team,
        team_cost__start=start,
        team_cost__end=end,
    ).select_related(
        "service_environment",
        "service_environment__service",
        "service_environment__environment",
    ):
        rows.append({
            "id": tsep.id,
            "service": tsep.service_environment.service.id,
            "env": tsep.service_environment.environment.id,
            "value": tsep.percent
        })
        total += tsep.percent
    return {
        "key": "teamDivision",
        "value": {
            "rows": rows,
            "total": total,
        },
    }


@csrf_exempt
@jsonify
@require_http_methods(["POST", "GET"])
def allocation_content(request, *args, **kwargs):
    first_day, last_day, days_in_month = get_dates(
        kwargs.get('year'),
        kwargs.get('month')
    )
    results = []
    if kwargs.get('service') != 'false' and kwargs.get('env') != 'false':
        results.append(
            _get_service_divison(
                kwargs.get('service'),
                kwargs.get('year'),
                kwargs.get('month'),
            )
        )
        results.append(
            _get_service_extra_cost(
                kwargs.get('service'),
                kwargs.get('env'),
                first_day,
                last_day,
            )
        )
    if kwargs.get('team') != 'false':
        results.append(
            _get_team_divison(
                kwargs.get('team'),
                first_day,
                last_day,
            )
        )
    return results


def _clear_daily_usages(
    pricing_objects,
    usage_type,
    first_day,
    last_day,
):
    daily_pricing_objects = DailyPricingObject.objects.filter(
        pricing_object__in=pricing_objects,
        date__gte=first_day,
        date__lte=last_day,
    )
    DailyUsage.objects.filter(
        date__gte=first_day,
        date__lte=last_day,
        daily_pricing_object__in=daily_pricing_objects,
        type=usage_type,
    ).delete()


@csrf_exempt
@jsonify
@require_http_methods(["POST"])
def allocation_save(request, *args, **kwargs):
    post_data = json.loads(request.raw_post_data)
    first_day, last_day, days_in_month = get_dates(
        post_data['year'],
        post_data['month'],
    )

    if kwargs.get('allocate_type') == 'servicedivision':
        service_usage_type = _get_service_usage_type(post_data['service'])
        pricing_objects = PricingObject.objects.filter(
            service_environment__service__id=post_data['service'],
            type=PRICING_OBJECT_TYPES.DUMMY,
        )
        _clear_daily_usages(
            pricing_objects,
            service_usage_type.usage_type,
            first_day,
            last_day,
        )
        for row in post_data['rows']:
            service_environment = ServiceEnvironment.objects.get(
                service__id=row['service'],
                environment__id=row['env'],
            )
            for day in xrange(days_in_month):
                iter_date = first_day + timedelta(days=day)
                for pricing_object in pricing_objects:
                    dpo = pricing_object.get_daily_pricing_object(iter_date)
                    DailyUsage.objects.get_or_create(
                        date=iter_date,
                        service_environment=service_environment,
                        daily_pricing_object=dpo,
                        value=row['value'],
                        type=service_usage_type.usage_type,
                    )
    if kwargs.get('allocate_type') == 'serviceextracost':
        service_environment = ServiceEnvironment.objects.get(
            service__id=post_data['service'],
            environment__id=post_data['env'],
        )
        ExtraCost.objects.filter(
            start=first_day,
            end=last_day,
            service_environment=service_environment,
        ).delete()
        for row in post_data['rows']:
            extra_cost = ExtraCost.objects.get_or_create(
                id=row.get('id'),
                start=first_day,
                end=last_day,
                service_environment=service_environment,
                extra_cost_type=ExtraCostType.objects.get(id=row['type']),
                defaults=dict(
                    cost=row['value']
                )
            )[0]
            extra_cost.cost = row['value']
            extra_cost.remarks = row.get('remarks', None)
            extra_cost.save()

    if kwargs.get('allocate_type') == 'teamdivision':
        try:
            team = Team.objects.get(id=post_data.get('team'))
        except Team.DoesNotExist:
            return {'status': False, 'message': 'Team Does Not Exist.'}
        TeamServiceEnvironmentPercent.objects.filter(
            team_cost__team=team,
            team_cost__start=first_day,
            team_cost__end=last_day,
        ).delete()
        team_cost = TeamCost.objects.get_or_create(
            team=team,
            start=first_day,
            end=last_day,
        )[0]
        for row in post_data['rows']:
            service_environment = ServiceEnvironment.objects.get(
                service__id=row.get('service'),
                environment__id=row.get('env')
            )
            tsep = TeamServiceEnvironmentPercent.objects.get_or_create(
                team_cost=team_cost,
                service_environment=service_environment,
                defaults=dict(
                    percent=row.get('value'),
                )
            )[0]
            tsep.percent = row.get('value')
            tsep.save()
    return {'status': True}


class AllocationClientContent(APIView):
    def get(self, request, service, env, year, month, format=None):
        return Response({
            'serviceDivision': {
                'total': 100,
                'name': 'Service division',
                'rows': [{'service': 97, 'env': 1, 'value': 100}],
                'template': 'tabservicedivision.html',
            },
            'serviceExtraCost': {
                'total': 400,
                'name': 'Extra Costs',
                'rows': [{'value': 400, 'description': 'test'}],
                'template': 'tabextracosts.html',
            },
        })


class AllocationClientDivision(APIView):
    def _get_service_usage_type(self, service):
        service = Service.objects.get(id=service)
        try:
            pricing_service = PricingService.objects.get(services=service)
        except:
            pricing_service = PricingService.objects.create(
                name=service.name + '_pricing_service',
                symbol=(
                    service.symbol or
                    service.name.lower().replace(' ', '_') + '_pricing_service'
                )
            )
            pricing_service.services.add(service)

        try:
            service_usage_type = ServiceUsageTypes.objects.get(
                pricing_service=pricing_service,
            )
        except:
            usage_type = UsageType.objects.create(
                name=service.name + '_usage_type',
                symbol=(
                    service.symbol or
                    service.name.lower().replace(' ', '_') + '_usage_type'
                ),
            )
            service_usage_type = ServiceUsageTypes.objects.create(
                usage_type=usage_type,
                pricing_service=pricing_service,
            )

        return service_usage_type

    def _get_service_divison(self, service, year, month, first_day):
        service_obj = Service.objects.get(id=service)
        service_usage_type = self._get_service_usage_type(service)
        daily_pricing_object = PricingObject.objects.filter(
            service_environment__service=service_obj,
            type=PRICING_OBJECT_TYPES.DUMMY,
        )[0].get_daily_pricing_object(first_day)

        rows = []
        total = 0
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
                "service": daily_usage.service_environment.service.id,
                "env": daily_usage.service_environment.environment.id,
                "value": daily_usage.value
            })
            total += daily_usage.value

        return rows, total


    def _get_service_extra_cost(self, service, env, start, end):
        extra_costs = ExtraCost.objects.filter(
            start=start,
            end=end,
            service_environment=ServiceEnvironment.objects.get(
                service__id=service,
                environment__id=env,
            )
        )
        rows = []
        for extra_cost in extra_costs:
            rows.append({
                "id": extra_cost.id,
                "type": extra_cost.extra_cost_type.id,
                "value": extra_cost.cost,
                "remarks": extra_cost.remarks,
            })
        extra_cost_types = []
        for extra_cost_type in ExtraCostType.objects.all():
            extra_cost_types.append({
                "name": extra_cost_type.name,
                "id": extra_cost_type.id
            })
        return rows, 999

    def get(self, request, *args, **kwargs):
        first_day, last_day, days_in_month = get_dates(
            kwargs.get('year'),
            kwargs.get('month')
        )
        division_rows, division_total = self._get_service_divison(
            kwargs.get('service'),
            kwargs.get('year'),
            kwargs.get('month'),
            first_day,
        )
        extracost_rows, extracost_total = self._get_service_extra_cost(
            kwargs.get('service'),
            kwargs.get('env'),
            first_day,
            last_day,
        )
        return Response({
            "serviceDivision": {
                "name": "Service Devision",
                "template": "tabservicedivision.html",
                "rows": division_rows,
                "total": division_total,
            },
            "serviceExtraCost": {
                "name": "Extra Cost",
                "template": "tabextracosts.html",
                "rows": extracost_rows,
                "total": extracost_total,
            },
        })
        # if kwargs.get('team'):
        #     results.append(
        #         _get_team_divison(
        #             kwargs.get('team'),
        #             first_day,
        #             last_day,
        #         )
        #     )


class AllocationClientPerTeam(APIView):
    def get(self, request, team, year, month, format=None):
        return Response({
            'teamDivision': {
                'total': 50,
                'name': 'Team division',
                'rows': [{'team': 1, 'value': 50}],
                'template': 'tabteamcosts.html',
            },
        })

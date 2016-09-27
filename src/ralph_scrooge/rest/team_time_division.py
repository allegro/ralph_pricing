# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.transaction import commit_on_success

from ralph_scrooge.rest.common import get_dates
from ralph_scrooge.models import (
    DailyUsage,
    ExtraCost,
    ExtraCostType,
    PricingService,
    Service,
    ServiceEnvironment,
    ServiceUsageTypes,
    Team,
    TeamCost,
    TeamServiceEnvironmentPercent,
    UsageType,
)

class TeamTimeDivisionSerializer(Serializer):
    team_id = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    division = PercentSerializer(many=True, required=True)


class DivizionSerializer(Serializer):
    service_uid = serializers.CharField(required=True)
    environment = serializers.CharField(required=True)
    percent = serializers.FloatField(required=True)


def _get_divisons(team, start, end):
    divisions = []
    for tsep in TeamServiceEnvironmentPercent.objects.filter(
        team_cost__team__id=team,
        team_cost__start=start,
        team_cost__end=end,
    ).select_related("service_environment"):
        divisions.append(
            new_division(
                tsep.service_environment.service_id,
                tsep.service_environment.environment_id,
                tsep.percent,
            )
        )
    return divisions


def new_division(service_uid, environment, percent):
    return {
        'service_uid': service_uid,
        'environment': environment,
        'percent': percent,
    }

class TeamTimeDivision(APIView):
    def get(self, request, year, month, team_id, *args, **kwargs):
        first_day, last_day, days_in_month = get_dates(year, month)
        return Response({
            "teamDivision": {
                "name": "Team Division",
                "template": "taballocationclientdivision.html",
                "rows": _get_team_divison(team_id, first_day, last_day),
            }
        })

    @commit_on_success()
    def post(self, request, year, month, team, *args, **kwargs):
        post_data = json.loads(request.raw_post_data)
        first_day, last_day, days_in_month = get_dates(year, month)

        try:
            team = Team.objects.get(id=team)
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

        return Response({"status": True})

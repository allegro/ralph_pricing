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


class PercentSerializer(Serializer):
    service_uid = serializers.CharField(required=True)
    environment = serializers.CharField(required=True)  # XXX ???
    percent = serializers.FloatField(required=True)

    def validate_service_uid(self, attrs, source):
        uid = attrs[source]
        if not Service.objects.filter(ci_uid=uid).exists():
            err = 'Service with UID {} does not exist.'.format(uid)
            raise serializers.ValidationError(err)
        return attrs


    def validate(self, attrs):
        err = None

        # validate service environment
        service_uid = attrs.get('service_uid')
        env = attrs.get('environment')
        if not ServiceEnvironment.objects.filter(
            service_ci_uid=service_uid,
            environment_name=env,
        ).exists():
            err = (
                'Service environment for service with UID "{}" and '
                'environment "{}" does not exist.'.format(service_uid, env)
            )

        # validate percents (if they sum up to 100)
        percent_total = 0
        for d in attrs.get('division'):
            percent_total += d['percent']
        if percent_total < 100:
            err = (
                "Percents should sum to 100, now it's {}."
                .format(percent_total)
            )

        if err is not None:
            raise serializers.ValidationError(err)  # XXX what about aggregating them?
        return attrs


def new_percent(service_uid, environment, percent):
    return {
        'service_uid': service_uid,
        'environment': environment,
        'percent': percent,
    }


def _get_percents(team, start, end):
    percents = []
    for tsep in TeamServiceEnvironmentPercent.objects.filter(
        team_cost__team__id=team,
        team_cost__start=start,
        team_cost__end=end,
    ).select_related("service_environment"):
        percents.append(
            new_percent(
                tsep.service_environment.service.ci_uid,
                tsep.service_environment.environment.name,
                tsep.percent,
            )
        )
    return percents


class TeamTimeDivisionSerializer(Serializer):
    team_id = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    division = PercentSerializer(many=True, required=True)

    def validate_team_id(self, attrs, source):
        team_id = attrs[source]
        # XXX
        return attrs

def new_team_time_division(team_id, year, month, division):
    return {
        'team_id': team_id,
        'year': year,
        'month': month,
        'division': division or [],
    }


class TeamTimeDivision(APIView):
    def get(self, request, year, month, team_id, *args, **kwargs):
        year = int(year)
        month = int(month)
        team_id = int(team_id)
        first_day, last_day, days_in_month = get_dates(year, month)
        percents = _get_percents(team_id, first_day, last_day)
        division = new_team_time_division(team_id, year, month, percents)
        serializer = TeamTimeDivisionSerializer(division)
        return Response(serializer.data)

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

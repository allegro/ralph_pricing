# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db.transaction import commit_on_success
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from ralph_scrooge.models import (
    Service,
    ServiceEnvironment,
    Team,
    TeamCost,
    TeamServiceEnvironmentPercent,
)
from ralph_scrooge.rest.auth import (
    IsTeamLeader,
    TastyPieLikeTokenAuthentication,
)
from ralph_scrooge.rest.common import get_dates


class PercentSerializer(Serializer):
    service_uid = serializers.CharField(required=True)
    environment = serializers.CharField(required=True)
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
            service__ci_uid=service_uid,
            environment__name=env,
        ).exists():
            err = (
                'Service environment for service with UID "{}" and '
                'environment "{}" does not exist.'.format(service_uid, env)
            )

        if err is not None:
            raise serializers.ValidationError(err)
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
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            err = "Team with ID {} does not exist.".format(team_id)
            raise serializers.ValidationError(err)
        # XXX(xor-xor) I don't like filling it here (team_id vs team).
        attrs[source] = team
        return attrs

    def validate(self, attrs):
        err = None

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
            raise serializers.ValidationError(err)
        return attrs


def new_team_time_division(team_id, year, month, division):
    return {
        'team_id': team_id,
        'year': year,
        'month': month,
        'division': division or [],
    }

@api_view(['GET'])
@authentication_classes((TastyPieLikeTokenAuthentication,))
@permission_classes((IsAuthenticated, IsTeamLeader))
def list_team_time_division(request, year, month, team_id, *args, **kwargs):
    year = int(year)
    month = int(month)
    team_id = int(team_id)
    first_day, last_day, days_in_month = get_dates(year, month)
    percents = _get_percents(team_id, first_day, last_day)
    division = new_team_time_division(team_id, year, month, percents)
    serializer = TeamTimeDivisionSerializer(division)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes((TastyPieLikeTokenAuthentication,))
@permission_classes((IsAuthenticated, IsTeamLeader))
def create_team_time_division(request, *args, **kwargs):
    serializer = TeamTimeDivisionSerializer(data=request.DATA)
    if serializer.is_valid():
        save_team_time_division(serializer.object)
        return HttpResponse(status=201)
    return Response(serializer.errors, status=400)


@commit_on_success()
def save_team_time_division(ttd):
    first_day, last_day, days_in_month = get_dates(ttd['year'], ttd['month'])

    # Previously uploaded division(s) for a given team and dates should be
    # removed.
    TeamServiceEnvironmentPercent.objects.filter(
        team_cost__team=ttd['team_id'],
        team_cost__start=first_day,
        team_cost__end=last_day,
    ).delete()

    team_cost = TeamCost.objects.get_or_create(
        team=ttd['team_id'],
        start=first_day,
        end=last_day,
    )[0]
    for percent in ttd['division']:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_uid=percent.get('service_uid'),
            environment__name=percent.get('environment')
        )
        tsep, created = TeamServiceEnvironmentPercent.objects.get_or_create(
            team_cost=team_cost,
            service_environment=service_environment,
            defaults=dict(percent=percent.get('percent'))
        )
        if not created:
            tsep.percent = percent.get('percent')
            tsep.save()

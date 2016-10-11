# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import Counter

from django.db.transaction import commit_on_success
from django.http import HttpResponse
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from ralph_scrooge.models import (
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

    def validate(self, attrs):
        err = None

        # Validate service environment (given indirectly by service_uid and
        # env).
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


def _get_percents(team_id, start, end):
    percents = []
    for tsep in TeamServiceEnvironmentPercent.objects.filter(
        team_cost__team=team_id,
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
    division = PercentSerializer(many=True, required=True)

    def validate_division(self, attrs, source):
        division = attrs[source]
        if division is None or len(division) == 0:
            raise serializers.ValidationError("This field cannot be empty.")
        return attrs

    def validate(self, attrs):
        err = None
        division = attrs.get('division')
        if division is None:
            return attrs

        # validate percents (if they sum up to 100)
        percent_total = 0
        for d in division:
            percent_total += d['percent']
        if percent_total != 100:
            err = (
                "Percents should sum to 100, now it's {}."
                .format(percent_total)
            )

        # validate uniqueness of service_uid/environment per single division
        uids_and_envs = [
            "{}/{}".format(
                d['service_uid'], d['environment']
            ) for d in division
        ]
        counter = Counter(uids_and_envs)
        non_unique = []
        for c in counter.items():
            if c[1] > 1:
                non_unique.append(c[0])
        if len(non_unique) > 0:
            err = (
                "Repeated service_uid/environment combination(s): {}."
                .format(', '.join(non_unique))
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


class TeamTimeDivision(APIView):
    authentication_classes = (TastyPieLikeTokenAuthentication,)
    permission_classes = (IsAuthenticated, IsTeamLeader)

    def get(self, request, year, month, team_id, *args, **kwargs):
        year, month, team_id = _args_to_int(year, month, team_id)
        try:
            Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            err = "Team with ID {} does not exist.".format(team_id)
            return Response(
                {'error': err}, status=status.HTTP_404_NOT_FOUND
            )
        first_day, last_day, days_in_month = get_dates(year, month)
        percents = _get_percents(team_id, first_day, last_day)
        division = new_team_time_division(team_id, year, month, percents)
        serializer = TeamTimeDivisionSerializer(division)
        return Response(serializer.data)

    def post(self, request, year, month, team_id, *args, **kwargs):
        year, month, team_id = _args_to_int(year, month, team_id)
        try:
            Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            err = "Team with ID {} does not exist.".format(team_id)
            return Response(
                {'error': err}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = TeamTimeDivisionSerializer(data=request.DATA)
        if serializer.is_valid():
            save_team_time_division(
                serializer.object['division'],
                year,
                month,
                team_id
            )
            return HttpResponse(status=201)
        return Response(serializer.errors, status=400)


def _args_to_int(*args):
    return tuple([int(arg) for arg in args])


@commit_on_success()
def save_team_time_division(division, year, month, team_id):
    first_day, last_day, days_in_month = get_dates(year, month)

    # Previously uploaded division(s) for a given team and dates should be
    # removed.
    TeamServiceEnvironmentPercent.objects.filter(
        team_cost__team=team_id,
        team_cost__start=first_day,
        team_cost__end=last_day,
    ).delete()

    team_cost = TeamCost.objects.get_or_create(
        team_id=team_id,
        start=first_day,
        end=last_day,
    )[0]
    for percent in division:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_uid=percent.get('service_uid'),
            environment__name=percent.get('environment')
        )
        TeamServiceEnvironmentPercent.objects.create(
            team_cost=team_cost,
            service_environment=service_environment,
            percent=percent.get('percent'),
        )

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date, timedelta
import calendar

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from drf_compound_fields.fields import DictField, ListField
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from ralph_scrooge.models import (
    DailyCost,
    ServiceEnvironment,
    UsageType,
)
from ralph_scrooge.rest.auth import IsServiceOwner

USAGE_COST_NUM_DIGITS = 2
USAGE_VALUE_NUM_DIGITS = 5


class ServiceEnvironmentsCostsDeserializer(Serializer):
    service_uid = serializers.CharField()
    environment = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    group_by = serializers.CharField()
    usage_types = ListField(serializers.CharField(), required=False)

    def validate_group_by(self, attrs, source):
        allowed_values = ('month', 'day')
        group_by = attrs[source]
        if group_by not in allowed_values:
            err = (
                'Unknown value: "{}". Allowed values for this field are: {}.'
                .format(group_by, ', '.join(
                    ['"{}"'.format(v) for v in allowed_values]
                ))
            )
            raise serializers.ValidationError(err)
        return attrs

    def validate_usage_types(self, attrs, source):
        usage_types = attrs.get(source)
        if usage_types is None or len(usage_types) == 0:
            attrs[source] = UsageType.objects.all()
            return attrs
        usage_types_validated = []
        unknown_values = []
        for ut in usage_types:
            try:
                # XXX @mkurek: Should we fetch them by `name` or by `symbol`?
                usage_types_validated.append(UsageType.objects.get(name=ut))
            except UsageType.DoesNotExist:
                unknown_values.append(ut)
        if len(unknown_values) > 0:
            err = (
                'Unknown value(s): {}.'.format(
                    ', '.join(['"{}"'.format(v) for v in unknown_values]),
                )
            )
            raise serializers.ValidationError(err)
        attrs[source] = usage_types_validated
        return attrs

    def validate(self, attrs):
        errors = []

        # Validate correctness of date range.
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        if date_from > date_to:
            errors.append("'date_from' should be less or equal to 'date_to'")

        # Validate service environment (given indirectly by service_uid and
        # environment).
        service_uid = attrs.get('service_uid')
        env = attrs.get('environment')
        try:
            service_env = ServiceEnvironment.objects.get(
                service__ci_uid=service_uid,
                environment__name=env,
            )
        except ServiceEnvironment.DoesNotExist:
            errors.append(
                'service environment for service with UID "{}" and '
                'environment "{}" does not exist'.format(service_uid, env)
            )
        else:
            attrs['_service_environment'] = service_env

        if len(errors) > 0:
            err_msg = '{}.'.format('; '.join(errors))
            raise serializers.ValidationError(err_msg)
        return attrs


class ComponentCostSerializer(Serializer):
    cost = serializers.FloatField()
    usage_value = serializers.FloatField()


class CostsSerializer(Serializer):
    total_cost = serializers.FloatField()
    usages = DictField(ComponentCostSerializer())


class DailyCostsSerializer(CostsSerializer):
    grouped_date = serializers.DateField()


class MonthlyCostsSerializer(CostsSerializer):
    grouped_date = serializers.DateField(format='%Y-%m')


class ServiceEnvironmentsDailyCostsSerializer(Serializer):
    costs = DailyCostsSerializer(many=True)


class ServiceEnvironmentsMonthlyCostsSerializer(Serializer):
    costs = MonthlyCostsSerializer(many=True)


# Taken from "Python Cookbook" (3rd edition).
def get_month_range(start_date=None):
    """Returns tuple (start_date, end_date), where the `end_date` is
    `start_date` plus one month. If `start_date` is not given, the first day
    of the current month (as per date.today()) is taken.
    """
    if start_date is None:
        start_date = date.today().replace(day=1)
    _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date + timedelta(days=days_in_month)
    return (start_date, end_date)


# Taken from "Python Cookbook" (3rd edition).
def date_range(start, stop, step=timedelta(days=1)):
    """This function is similar to "normal" `range`, but it operates on dates
    instead of numbers.
    """
    while start < stop:
        yield start
        start += step


def month_range(start, stop):
    """A variant of `date_range`, with `step` param set to 1 month.
    The `start` and `stop` dates will have `day` component reset to `1`.
    """
    start = start.replace(day=1)
    stop = stop.replace(day=1)
    return date_range(start, stop, step=relativedelta(months=1))


def round_safe(value, precision):
    """Standard `round` function raises TypeError when None is given as value
    to. This function just ignores such values (i.e., returns them unmodified).
    """
    if value is None:
        return value
    return round(value, precision)


def fetch_costs_per_month(
        service_env, usage_types, date_from, date_to, round_to_month=False
):
    """Fetch DailyCosts associated with given `service_env` and
    `usage_types`, in range defined by `date_from` and `date_to`, and
    summarize them per-month (i.e. their `value` and `cost` fields).
    The result of such single summarization looks like this:

        {
            "grouped_date": "2016-10",
            "total_cost": 14143.68,
            "usages": {
                "some_usage_type1": {
                    "cost": 35.68,
                    "usage_value": 35.68
                },
                "some_usage_type2": {
                    "cost": 14108.0,
                    "usage_value": 7054.0
                }
                ...
            }
        }

    Such results are collected into a list, and that list is wrapped into a
    dict, under the `costs` key  - and that dict is returned as a final result.

    And while the aforementioned costs are summarized only for selected usage
    types, the value in `total_cost` field contains sum of costs associated
    with *all* usage types for a given service environment / date range
    combination - so if there are no such "other" costs, this value should be
    equal to the sum of `cost` fields above.

    The `round_to_month` param, when set to True, rounds `date_from` and
    `date_to` to month boundaries, i.e. costs from periods:

        <first day of the month> to `date_from`

    and:

        `date_to` to <last day of the month>

    ...are also taken into calculations.

    It is also worth mentioning, that precision of fields `total_cost`, `cost`
    and `usage_values` is controlled by `USAGE_COST_NUM_DIGITS` and
    `USAGE_VALUE_NUM_DIGITS` defined in this module.
    """
    costs = {
        'costs': [],
    }
    a_month = relativedelta(months=1)
    a_day = timedelta(days=1)
    for date_ in month_range(date_from, date_to + a_month):
        first_day, last_day = get_month_range(start_date=date_)

        if not round_to_month:
            if (
                first_day.year == date_from.year and
                first_day.month == date_from.month and
                date_from.day > first_day.day
            ):
                first_day = date_from
            if (
                (last_day - a_day).year == date_to.year and
                (last_day - a_day).month == date_to.month and
                date_to.day < (last_day - a_day).day
            ):
                last_day = (date_to + a_day)

        current_day = first_day
        total_cost_for_month = 0
        usages_dict = {}
        for usage_type in usage_types:
            usages_dict[usage_type] = {
                'cost': 0,
                'usage_value': 0,
            }

        while (current_day < last_day):
            total_cost_for_day = DailyCost.objects.filter(
                service_environment=service_env,
                date=current_day,
            ).aggregate(Sum('cost'))['cost__sum']
            if total_cost_for_day is not None:
                total_cost_for_month += total_cost_for_day

            for usage_type in usage_types:
                cost_and_value = DailyCost.objects_tree.filter(
                    service_environment=service_env,
                    date=current_day,
                    type=usage_type
                ).aggregate(usage_value=Sum('value'), cost=Sum('cost'))

                cost = cost_and_value['cost']
                usage_value = cost_and_value['usage_value']
                if cost is not None:
                    usages_dict[usage_type]['cost'] += cost
                if usage_value is not None:
                    usages_dict[usage_type]['usage_value'] += usage_value

            current_day += a_day

        for k, v in usages_dict.iteritems():
            usages_dict[k] = {
                'cost': round_safe(v['cost'], USAGE_COST_NUM_DIGITS),
                'usage_value': round_safe(
                    v['usage_value'], USAGE_VALUE_NUM_DIGITS
                ),
            }

        cost = {
            'grouped_date': date_,
            'total_cost': round_safe(
                total_cost_for_month, USAGE_COST_NUM_DIGITS
            ),
            'usages': usages_dict,
        }

        costs['costs'].append(cost)
    return costs


def fetch_costs_per_day(service_env, usage_types, date_from, date_to):
    """A simpified variant of `fetch_costs_per_month` that summarizes
    costs per-day. The only difference in resulting data structures,
    apart values, is the format of `grouped_date` field - in
    `fetch_costs_per_month` it will look like "2016-10-01", but here,
    the day component is stripped, so it will be "2016-10" instead.

    """
    costs = {
        'costs': [],
    }

    for date_ in date_range(date_from, date_to + timedelta(days=1)):
        total_cost_for_day = DailyCost.objects.filter(
            service_environment=service_env,
            date=date_,
        ).aggregate(Sum('cost'))['cost__sum']

        usages_and_costs = {}
        for usage_type in usage_types:
            cost_and_value = DailyCost.objects_tree.filter(
                service_environment=service_env,
                date=date_,
                type=usage_type
            ).aggregate(usage_value=Sum('value'), cost=Sum('cost'))
            usages_and_costs[usage_type] = cost_and_value

        cost = {
            'grouped_date': date_,
            'total_cost': round_safe(
                total_cost_for_day, USAGE_COST_NUM_DIGITS
            ),
            'usages': {},
        }
        for k, v in usages_and_costs.iteritems():
            cost['usages'][k] = {
                'cost': round_safe(v['cost'], USAGE_COST_NUM_DIGITS),
                'usage_value': round_safe(
                    v['usage_value'], USAGE_VALUE_NUM_DIGITS
                ),
            }
        costs['costs'].append(cost)
    return costs


class ServiceEnvironmentsCosts(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsServiceOwner)

    def post(self, request, *args, **kwargs):
        deserializer = ServiceEnvironmentsCostsDeserializer(data=request.DATA)

        # A workaround for ListField validation (from drf_compound_fields) that
        # for some reason can't handle nulls gracefully (it gives TypeError
        # instead of ValidationError or something like that).
        # This workaround can be removed once we switch to DjRF 3.x and get rid
        # of drf_compound_fields.
        if request.DATA.get('usage_types') is None:
            request.DATA['usage_types'] = []

        if deserializer.is_valid():
            service_env = deserializer.object['_service_environment']
            usage_types = deserializer.object['usage_types']
            date_from = deserializer.object['date_from']
            date_to = deserializer.object['date_to']

            if deserializer.object['group_by'] == 'day':
                costs = fetch_costs_per_day(
                    service_env, usage_types, date_from, date_to
                )
                return Response(
                    ServiceEnvironmentsDailyCostsSerializer(costs).data
                )
            if deserializer.object['group_by'] == 'month':
                costs = fetch_costs_per_month(
                    service_env, usage_types, date_from, date_to
                )
                return Response(
                    ServiceEnvironmentsMonthlyCostsSerializer(costs).data
                )

        return Response(deserializer.errors, status=400)

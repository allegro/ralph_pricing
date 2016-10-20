# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date, datetime, timedelta
import calendar

from dateutil.relativedelta import relativedelta
from django.db import connection
from django.db.models import Sum
from drf_compound_fields.fields import DictField, ListField
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from ralph_scrooge.models import (
    BaseUsage,
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
    group_by = serializers.CharField(default='day')
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
                usage_types_validated.append(BaseUsage.objects.get(symbol=ut))
            except BaseUsage.DoesNotExist:
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


# Not very elegant, but DjRF doesn't allow declaring recursive fields in
# "normal" way. BTW, this workaround allows only one level of recursion,
# but it is enough for our usage-case. In case you'd need more, you may be
# better off with `django-rest-framework-recursive` package, or something
# like that.
ComponentCostSerializer.base_fields['subcosts'] = DictField(
    ComponentCostSerializer()
)


class CostsSerializer(Serializer):
    total_cost = serializers.FloatField()
    costs = DictField(ComponentCostSerializer())


class DailyCostsSerializer(CostsSerializer):
    grouped_date = serializers.DateField()


class MonthlyCostsSerializer(CostsSerializer):
    grouped_date = serializers.DateField(format='%Y-%m')


class ServiceEnvironmentsDailyCostsSerializer(Serializer):
    service_environment_costs = DailyCostsSerializer(many=True)


class ServiceEnvironmentsMonthlyCostsSerializer(Serializer):
    service_environment_costs = MonthlyCostsSerializer(many=True)


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


def aggregate_costs(qs, usage_type, results, group_by):
    truncate_date = connection.ops.date_trunc_sql(group_by, 'date')  # XXX needed?
    qs = qs.extra({group_by: truncate_date})  # XXX needed?
    qs_by_usage_type = qs.filter(type=usage_type)
    if qs_by_usage_type.exists():
        # We assume that all elements in `qs_by_usage_type` have the same
        # `path` attribute - hence we need to check only the first one of them.
        path = qs_by_usage_type[0].path
    results_by_date = qs_by_usage_type.values(group_by).annotate(
        Sum('cost'), Sum('value')
    ).order_by(group_by)
    for r in results_by_date:
        d = _get_truncated_date(r[group_by])
        cost_and_usage_dict = {
            path: {
                '_usage_type_symbol': usage_type.symbol,
                'cost': r['cost__sum'],
                'usage_value': r['value__sum']
            }
        }
        if results.get(d) is not None:
             results[d].update(cost_and_usage_dict)
        else:
            results[d] = cost_and_usage_dict


def merge_costs_with_subcosts(costs, subcosts):
    merged_costs = {}
    for cost_path, cost_dict in costs.iteritems():
        usage_type_symbol = cost_dict.pop('_usage_type_symbol')
        merged_costs[usage_type_symbol] = cost_dict
        merged_costs[usage_type_symbol]['subcosts'] = {}
        for subcost_path, subcost_dict in subcosts.iteritems():
            if subcost_path.split('/')[0] == cost_path:
                merged_costs[usage_type_symbol]['subcosts'].update(
                    {subcost_dict.pop('_usage_type_symbol'): subcost_dict}
                )
    return merged_costs


def _get_truncated_date(date_):
    """This function is just a workaround for sqlite, where
    `date_trunc_sql` has slightly different result than on e.g. MySQL
    (returned date is a string, not a datetime object).
    Considering that `date_trunc_sql` has been replaced with
    functions like TruncMonth in Django 1.10, this workaround should
    be considered as temporary.
    """
    try:
        d = date_.date()
    except AttributeError:
        d = datetime.strptime(date_, '%Y-%m-%d %H:%M:%S').date()
    return d


def get_total_costs(qs, group_by):
    total_costs = {}
    results = qs.filter(depth=0).values(group_by).annotate(
        Sum('cost')
    ).order_by(group_by)
    for r in results:
        d = _get_truncated_date(r[group_by])
        total_costs[d] = r['cost__sum']
    return total_costs


def fetch_costs(service_env, usage_types, date_from, date_to, group_by):
    # TODO(xor-xor): After switching to Django >= 1.10 `date_trunc_sql` and
    # `extra` won't be available, so use this:
    # http://stackoverflow.com/a/8746532/5768173.
    truncate_date = connection.ops.date_trunc_sql(group_by, 'date')
    initial_qs = DailyCost.objects_tree.filter(
        service_environment=service_env,
        date__gte=date_from,
        date__lte=date_to,
    )
    qs = initial_qs.extra({group_by: truncate_date})
    total_costs = get_total_costs(qs, group_by)
    results = {}
    for usage_type in usage_types:
        aggregate_costs(qs, usage_type, results, group_by)

    # Check for subcosts basing on usage types present in `initial_qs`.
    results_subcosts = {}
    if initial_qs.exists() and initial_qs[0].depth == 0:
        subcosts_qs = initial_qs.filter(
            path__startswith=initial_qs[0].path,
            depth=1
        )
        usage_types = set([subcost.type.usagetype for subcost in subcosts_qs])
        for usage_type in usage_types:
            aggregate_costs(
                subcosts_qs, usage_type, results_subcosts, group_by
            )

    # Construct final result (fill missing days/months, round values, match
    # subcosts with their parents etc.).
    final_result = {
        'service_environment_costs': []
    }
    if group_by == 'month':
        delta = relativedelta(months=1)
        date_range_ = date_range(
            date_from.replace(day=1),
            date_to.replace(day=1) + delta,
            step=delta
        )
    else:  # 'day' is default for `group_by` anyway
        delta = timedelta(days=1)
        date_range_ = date_range(
            date_from,
            date_to + delta,
            step=delta
        )
    for date_ in date_range_:
        total_cost_for_date = total_costs.get(date_, 0)
        costs = merge_costs_with_subcosts(
            results.get(date_, {}), results_subcosts.get(date_, {})
        )
        costs_for_date = {
            'grouped_date': date_,
            'total_cost': round_safe(
                total_cost_for_date, USAGE_COST_NUM_DIGITS
            ),
            'costs': _round_recursive(costs),
        }
        final_result['service_environment_costs'].append(costs_for_date)
    return final_result


# def fetch_costs_per_month(
#         service_env, usage_types, date_from, date_to, round_to_month=False
# ):

#      """Fetch DailyCosts associated with given `service_env` and
#     `usage_types`, in range defined by `date_from` and `date_to`, and
#     summarize them per-month (i.e. their `value` and `cost` fields).
#     The result of such single summarization looks like this:

#         {
#             "grouped_date": "2016-10",
#             "total_cost": 1400.00,
#             "usages": {
#                 "some_usage_type1": {
#                     "cost": 50.00,
#                     "usage_value": 10.00,
#                     "subcosts": {}
#                 },
#                 "some_usage_type2": {
#                     "cost": 300.0,
#                     "usage_value": 0.0
#                     "subcosts": {
#                         # we assume that only one level of nesting is possible
#                         # here (i.e., that there are no sub-subcosts)
#                         "some_usage_type3": {
#                             "cost": 100.00,
#                             "usage_value": 10.00
#                         },
#                         "some_usage_type4": {
#                             "cost": 200.00,
#                             "usage_value": 20.10
#                         }
#                     }
#                 }
#                 ...
#             }
#         }

#     Such results are collected into a list, and that list is wrapped into a
#     dict, under the `service-environment-costs` key  - and that dict is returned as a final result.

#     And while the aforementioned costs are summarized only for selected usage
#     types, the value in `total_cost` field contains sum of costs associated
#     with *all* usage types for a given service environment / date range
#     combination - so if there are no such "other" costs, this value should be
#     equal to the sum of `cost` fields above.

#     The `round_to_month` param, when set to True, rounds `date_from` and
#     `date_to` to month boundaries, i.e. costs from periods:

#         <first day of the month> to `date_from`

#     and:

#         `date_to` to <last day of the month>

#     ...are also taken into calculations.

#     It is also worth mentioning, that precision of fields `total_cost`, `cost`
#     and `usage_values` is controlled by `USAGE_COST_NUM_DIGITS` and
#     `USAGE_VALUE_NUM_DIGITS` defined in this module.
#     """
#     costs = {
#         'costs': [],
#     }
#     a_month = relativedelta(months=1)
#     a_day = timedelta(days=1)
#     for date_ in month_range(date_from, date_to + a_month):
#         first_day, last_day = get_month_range(start_date=date_)

#         if not round_to_month:
#             if (
#                 first_day.year == date_from.year and
#                 first_day.month == date_from.month and
#                 date_from.day > first_day.day
#             ):
#                 first_day = date_from
#             # This "arithmetic" on days below comes from the fact that
#             # `month_range` is semantically close to "normal" `range` (i.e.
#             # the end value is excluded - hence `date_to + a_month` as a 2nd
#             # argument), so we are always +1 here on days.
#             if (
#                 (last_day - a_day).year == date_to.year and
#                 (last_day - a_day).month == date_to.month and
#                 date_to.day < (last_day - a_day).day
#             ):
#                 last_day = (date_to + a_day)

#         current_day = first_day
#         total_cost_for_month = 0
#         usages_dict = {}
#         for usage_type in usage_types:
#             usages_dict[usage_type.symbol] = {
#                 'cost': 0,
#                 'usage_value': 0,
#             }

#         while (current_day < last_day):
#             total_cost_for_day = DailyCost.objects.filter(
#                 service_environment=service_env,
#                 date=current_day,
#             ).aggregate(Sum('cost'))['cost__sum']
#             if total_cost_for_day is not None:
#                 total_cost_for_month += total_cost_for_day

#             for usage_type in usage_types:
#                 cost_and_value = DailyCost.objects_tree.filter(
#                     service_environment=service_env,
#                     date=current_day,
#                     type=usage_type
#                 ).aggregate(usage_value=Sum('value'), cost=Sum('cost'))

#                 cost = cost_and_value['cost']
#                 usage_value = cost_and_value['usage_value']
#                 if cost is not None:
#                     usages_dict[usage_type.symbol]['cost'] += cost
#                 if usage_value is not None:
#                     usages_dict[usage_type.symbol]['usage_value'] += usage_value  # noqa: E501

#             current_day += a_day

#         # for k, v in usages_dict.iteritems():
#         #     usages_dict[k] = {
#         #         'cost': round_safe(v['cost'], USAGE_COST_NUM_DIGITS),
#         #         'usage_value': round_safe(
#         #             v['usage_value'], USAGE_VALUE_NUM_DIGITS
#         #         ),
#         #     }

#         cost = {
#             'grouped_date': date_,
#             'total_cost': round_safe(
#                 total_cost_for_month, USAGE_COST_NUM_DIGITS
#             ),
#             'costs': _round_recursive(usages_dict),  # XXX usages_and_costs?
#         }

#         costs['service_environment_costs'].append(cost)
#     return costs


def _fetch_subcosts(parent_qs, service_env, date_):
    """`depth == 0` means that we are dealing with a potential parent, so we
    need to check if it has any children - and for that we employ the fact
    that children's `path` always start with parent's path.
    We also assume three things here:
    1) that the maximum possible nesting in costs is one level;
    2) that all members of the queryset `parent_qs` have `depth` == 0;
    3) that all members of the queryset `parent_qs` have the same `path`
       component (i.e., they are the same BaseUsage objects; BTW, the numbers
       visible in `path` field - e.g. "484/483" are the IDs of BaseUsage).
    """
    if parent_qs.exists() and parent_qs[0].depth == 0:
        # Fetch all children, ignore differences in usage_type for now.
        subcosts_qs = DailyCost.objects_tree.filter(
            service_environment=service_env,
            date=date_,
            path__startswith=parent_qs[0].path,
            depth=1
        )

        # Filter `subcosts_qs` by usage_type and preform cost/usage_value
        # aggregation as in "normal" (i.e. top-level) costs.
        usage_types = set([subcost.type.usagetype for subcost in subcosts_qs])
        subcosts = {}
        for usage_type in usage_types:
            qs = subcosts_qs.filter(
                service_environment=service_env,
                date=date_,
                type=usage_type
            )
            cost_and_value = qs.aggregate(
                usage_value=Sum('value'), cost=Sum('cost')
            )
            subcosts[usage_type.symbol] = cost_and_value
        return subcosts


def _round_recursive(usages_and_costs):
    """Performs rounding of values in `cost` and `usage_value` fields. And
    because `usages_and_costs` dict can be actually a tree (costs having
    subcosts), it does that in a recursive manner.
    """
    rounded = {}
    if usages_and_costs is not None:
        for k, v in usages_and_costs.iteritems():
            rounded[k] = {
                'cost': round_safe(v['cost'], USAGE_COST_NUM_DIGITS),
                'usage_value': round_safe(
                    v['usage_value'], USAGE_VALUE_NUM_DIGITS
                ),
                'subcosts': _round_recursive(v.get('subcosts', {})),
            }
    return rounded


def fetch_costs_per_day(service_env, usage_types, date_from, date_to):
    """A simpified variant of `fetch_costs_per_month` that summarizes
    costs per-day. The only difference in resulting data structures,
    apart values, is the format of `grouped_date` field - in
    `fetch_costs_per_month` it will look like "2016-10-01", but here,
    the day component is stripped, so it will be "2016-10" instead.

    """

    costs = {
        'service_environment_costs': [],
    }

    for date_ in date_range(date_from, date_to + timedelta(days=1)):
        total_cost_for_day = DailyCost.objects.filter(
            service_environment=service_env,
            date=date_,
        ).aggregate(Sum('cost'))['cost__sum']

        usages_and_costs = {}
        for usage_type in usage_types:
            qs = DailyCost.objects_tree.filter(
                service_environment=service_env,
                date=date_,
                type=usage_type
            )
            cost_and_value = qs.aggregate(
                usage_value=Sum('value'), cost=Sum('cost')
            )
            cost_and_value['subcosts'] = _fetch_subcosts(
                qs, service_env, date_
            )
            usages_and_costs[usage_type.symbol] = cost_and_value

        cost = {
            'grouped_date': date_,
            'total_cost': round_safe(
                total_cost_for_day, USAGE_COST_NUM_DIGITS
            ),
            'costs': _round_recursive(usages_and_costs),
        }
        costs['service_environment_costs'].append(cost)
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
            group_by = deserializer.object['group_by']

            # XXX
            if group_by == 'day':
                costs = fetch_costs(
                    service_env, usage_types, date_from, date_to, group_by
                )
                return Response(
                    ServiceEnvironmentsDailyCostsSerializer(costs).data
                )
            if group_by == 'month':
                costs = fetch_costs(
                    service_env, usage_types, date_from, date_to, group_by
                )
                return Response(
                    ServiceEnvironmentsMonthlyCostsSerializer(costs).data
                )

        return Response(deserializer.errors, status=400)

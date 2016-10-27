# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta

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
from ralph_scrooge.utils.cache import memoize

USAGE_COST_NUM_DIGITS = 2
USAGE_VALUE_NUM_DIGITS = 5
GROUP_BY_CHOICES = (
    ('day', 'day'),
    ('month', 'month'),
)


@memoize
def get_valid_usage_types():
    """We are interested here in all types except "SU" which is "Service usage
    type" (see TYPE_CHOICES in ralph_scrooge.models.usage).
    """
    return BaseUsage.objects.exclude(
        pk__in=UsageType.objects.filter(usage_type='SU')
    )


class ServiceEnvironmentCostsDeserializer(Serializer):
    service_uid = serializers.CharField()
    environment = serializers.CharField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    group_by = serializers.ChoiceField(choices=GROUP_BY_CHOICES)
    usage_types = ListField(serializers.CharField(), required=False)

    def validate_usage_types(self, attrs, source):
        valid_usage_types = get_valid_usage_types()
        usage_types = attrs.get(source)
        if usage_types is None or len(usage_types) == 0:
            attrs[source] = valid_usage_types
            return attrs
        usage_types_validated = []
        unknown_values = []
        for ut in usage_types:
            try:
                usage_types_validated.append(valid_usage_types.get(symbol=ut))
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


class ServiceEnvironmentDailyCostsSerializer(Serializer):
    service_environment_costs = DailyCostsSerializer(many=True)


class ServiceEnvironmentMonthlyCostsSerializer(Serializer):
    service_environment_costs = MonthlyCostsSerializer(many=True)


def date_range(start, stop, step=timedelta(days=1)):
    """This function is similar to "normal" `range`, but it operates on dates
    instead of numbers. Taken from "Python Cookbook, 3rd ed.".
    """
    while start < stop:
        yield start
        start += step


def round_safe(value, precision):
    """Standard `round` function raises TypeError when None is given as value
    to. This function just ignores such values (i.e., returns them unmodified).
    """
    if value is None:
        return value
    return round(value, precision)


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


def _get_total_costs(qs, group_by):
    """Sums `cost` fields by time period given as `group_by` (i.e. "day",
    "month"), in queryset given as `qs`.

    Please note that only top-level costs (i.e. with `depth` == 0),
    even those that are not selected explicitly with `usage_types`
    (see `fetch_costs`) are taken into account here - hence "total
    costs" in its name.
    """
    total_costs = {}
    results = qs.filter(depth=0).values(group_by).annotate(
        Sum('cost')
    ).order_by(group_by)
    for r in results:
        d = _get_truncated_date(r[group_by])
        total_costs[d] = r['cost__sum']
    return total_costs


def _aggregate_costs(qs, usage_type, group_by, results):
    """Aggregate costs from queryset `qs`, which is filtered by `usage_type`
    and then grouped by date period given as `group_by` (e.g., "day", "month").
    `results` argument is a dictionary, where results of this function are
    appended (i.e., this function doesn't return anything).
    """
    # XXX(xor-xor): Check if truncate_date is really needed here.
    truncate_date = connection.ops.date_trunc_sql(group_by, 'date')
    qs_with_truncate_date = qs.extra({group_by: truncate_date})
    qs_by_usage_type = qs_with_truncate_date.filter(type=usage_type)
    # We use `len` instead of `exists` or `count` because of a bug in older
    # Django, see: http://stackoverflow.com/q/37446551/5768173.
    if len(qs_by_usage_type) > 0:
        # We assume that all elements in `qs_by_usage_type` have the same
        # `path` attribute - hence `qs_by_usage_type[0]`.
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


def _merge_costs_with_subcosts(costs, subcosts):
    """Merge `costs` and `subcosts` dicts, where matching is done via
    `path` attribute. E.g., having subcost with path "484/483" and
    cost with path "484", it means that the former should be merged
    with the latter.
    """
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


def _fetch_subcosts(parent_qs, service_env, date_):
    """Fetches (and aggregate) subcosts basing on the fact that children's
    `path` always start with parent's `path` (e.g., "484/483" and "484").

    We assume three things here:
    1) that the maximum possible nesting in costs is one level;
    2) that all members of the queryset `parent_qs` have `depth` == 0;
    3) that all members of the queryset `parent_qs` have the same `path`
       component (i.e., they are the same BaseUsage objects).
    """
    # We use `len` instead of `exists` or `count` because of a bug in older
    # Django, see: http://stackoverflow.com/q/37446551/5768173.
    if len(parent_qs) > 0 and parent_qs[0].depth == 0:
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


def fetch_costs_alt(service_env, usage_types, date_from, date_to, group_by):
    """An alternative version of `fetch_costs` function. The difference is that
    it makes less DB queries, so in theory it should be faster (to be confirmed
    with performance tests).
    """
    # TODO(xor-xor): Remember to remove `fetch_costs` or `fetch_costs_alt`
    # function (with dependencies) once we have results of the aforementioned
    # performance tests.
    truncate_date = connection.ops.date_trunc_sql(group_by, 'date')
    initial_qs = DailyCost.objects_tree.filter(
        date__gte=date_from,
        date__lte=date_to,
        service_environment=service_env,
    ).extra({group_by: truncate_date})

    total_costs = _get_total_costs(initial_qs, group_by)

    aggregated_costs = initial_qs.values_list(
        group_by, 'path', 'type__symbol'
    ).annotate(
        cost_sum=Sum('cost'), value_sum=Sum('value')
    )

    cost_trees = _create_trees(aggregated_costs)
    cost_trees_ = _replace_path_with_type_symbol(cost_trees)

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
    else:
        # 'day' is default for `group_by` anyway so it's OK to use it
        # as a fallback here.
        delta = timedelta(days=1)
        date_range_ = date_range(
            date_from,
            date_to + delta,
            step=delta
        )
    for date_ in date_range_:
        total_cost_for_date = total_costs.get(date_, 0)
        costs_for_date = {
            'grouped_date': date_,
            'total_cost': round_safe(
                total_cost_for_date, USAGE_COST_NUM_DIGITS
            ),
            'costs': _round_recursive(cost_trees_.get(date_, {})),
        }
        final_result['service_environment_costs'].append(costs_for_date)
    return final_result


def _create_trees(aggregated_costs):
    """From `aggregated_costs`, where each item (`ac`) has the following (flat)
    structure:

    ac[0]: date, e.g. datetime.datetime(2016, 10, 7, 0, 0)
    ac[1]: path, e.g. '484/483'
    ac[2]: base usage type symbol, e.g. 'subtype2'
    ac[3]: cost, e.g. Decimal('222.00')
    ac[4]: usage value, e.g. 2.0

    ...create a dict `cost_trees`, where each entry is a tree with the
    following form:

    datetime.date(2016, 10, 7): {
        '484': {
            '_type_symbol': 'type1',
            'cost': Decimal('333.00'),
            'usage_value': 0.0,
            'subcosts': {  #  subcosts are optional
                '484/482': {
                    '_type_symbol': 'subtype1',
                    'cost': Decimal('111.00'),
                    'usage_value': 1.0
                },
                '484/483': {
                    '_type_symbol': 'subtype2',
                    'cost': Decimal('222.00'),
                    'usage_value': 2.0
                }
            }
        }
    }

    The pairing between costs and subcosts is done via the path component (e.g.
    a cost with '484/483' is a subcost of '484').
    """
    cost_trees = {}
    for ac in aggregated_costs:
        date_ = _get_truncated_date(ac[0])
        d = {
            ac[1]: {
                '_type_symbol': ac[2],
                'cost': ac[3],
                'usage_value': ac[4],
            }
        }
        if "/" in ac[1]:
            parent = ac[1].split("/")[0]
            if cost_trees[date_].get(parent) is None:
                cost_trees[date_][parent] = {'subcosts': d}
            else:
                if cost_trees[date_][parent].get('subcosts') is None:
                    cost_trees[date_][parent]['subcosts'] = d
                else:
                    cost_trees[date_][parent]['subcosts'].update(d)
        else:
            d[ac[1]].update({'subcosts': {}})
            if cost_trees.get(date_) is None:
                cost_trees[date_] = d
            else:
                cost_trees[date_].update(d)
    return cost_trees


def _replace_path_with_type_symbol(cost_trees):
    """Having a dict with cost trees (for the description of its structure
    see `_create_trees` function`), replace path components (e.g. '484',
    '484/482', '484/483') with the contents of the `_type_symbol` field and
    finally remove that field.
    So in the case described in `create_trees`, '484' will become 'type1',
    '484/482' will become 'subtype1' and '484/483' will be 'subtype2'.
    """
    cost_trees_ = {}
    tmp_dict = {}
    for k, v in cost_trees.items():
        if k == 'subcosts':
            for kk, vv in v.items():
                type_symbol = vv.pop('_type_symbol')
                d = {type_symbol: vv}
                if tmp_dict.get(k) is not None:
                    tmp_dict[k].update(d)
                else:
                    tmp_dict[k] = d
        elif type(v) == dict:
            for kk, vv in v.items():
                type_symbol = vv.pop('_type_symbol')
                cost_trees_[k] = {
                    type_symbol: _replace_path_with_type_symbol(vv)
                }
        else:
            tmp_dict[k] = v
    cost_trees_.update(tmp_dict)
    return cost_trees_


def fetch_costs(service_env, usage_types, date_from, date_to, group_by):
    """Fetch DailyCosts associated with given `service_env` and
    `usage_types`, in range defined by `date_from` and `date_to`, and
    summarize them (i.e. their `value` and `cost` fields) per period given by
    `group_by` (e.g. "day" or "month").

    The result of such single summarization looks like this:

        {
            "grouped_date": "2016-10",  # or "2016-10-01" when group by day
            "total_cost": 1400.00,
            "usages": {
                "some_usage_type1": {
                    "cost": 50.00,
                    "usage_value": 10.00,
                    "subcosts": {}
                },
                "some_usage_type2": {
                    "cost": 300.0,
                    "usage_value": 0.0
                    "subcosts": {
                        # we assume that only one level of nesting is possible
                        # here (i.e., that there are no sub-subcosts)
                        "some_usage_type3": {
                            "cost": 100.00,
                            "usage_value": 10.00
                        },
                        "some_usage_type4": {
                            "cost": 200.00,
                            "usage_value": 20.10
                        }
                    }
                }
                ...
            }
        }

    Such results are collected into a list, and that list is wrapped
    into a dict, under the `service-environment-costs` key - and that
    dict is returned as a final result.

    And while the aforementioned costs are summarized only for selected usage
    types, the value in `total_cost` field contains sum of costs associated
    with *all* usage types for a given service environment / date range
    combination - so if there are no such "other" costs, this value should be
    equal to the sum of `cost` fields above.

    It is also worth mentioning, that precision of fields `total_cost`, `cost`
    and `usage_values` is controlled by `USAGE_COST_NUM_DIGITS` and
    `USAGE_VALUE_NUM_DIGITS` defined in this module.
    """

    # TODO(xor-xor): After switching to Django >= 1.10 `date_trunc_sql` and
    # `extra` won't be available, so use this:
    # http://stackoverflow.com/a/8746532/5768173.

    # Prepare querysets and perform aggregations on them.
    truncate_date = connection.ops.date_trunc_sql(group_by, 'date')
    initial_qs = DailyCost.objects_tree.filter(
        service_environment=service_env,
        date__gte=date_from,
        date__lte=date_to,
    )
    qs = initial_qs.extra({group_by: truncate_date})
    total_costs = _get_total_costs(qs, group_by)
    results = {}
    for usage_type in usage_types:
        _aggregate_costs(qs, usage_type, group_by, results)

    # Check for subcosts basing on usage types present in `initial_qs`.
    results_subcosts = {}
    for usage_type in usage_types:
        qs = initial_qs.filter(type=usage_type)
        # We use `len` instead of `exists` or `count` because of a bug in older
        # Django, see: http://stackoverflow.com/q/37446551/5768173.
        if len(qs) > 0 and qs[0].depth == 0:
            subcosts_qs = initial_qs.filter(
                path__startswith=qs[0].path,
                depth=1
            )
            usage_types_ = set(
                [subcost.type.usagetype for subcost in subcosts_qs]
            )
            for usage_type_ in usage_types_:
                _aggregate_costs(
                    subcosts_qs, usage_type_, group_by, results_subcosts
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
        costs = _merge_costs_with_subcosts(
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


class ServiceEnvironmentCosts(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsServiceOwner)

    def post(self, request, *args, **kwargs):
        deserializer = ServiceEnvironmentCostsDeserializer(data=request.DATA)

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

            costs = fetch_costs_alt(
                service_env, usage_types, date_from, date_to, group_by
            )
            if group_by == 'day':
                return Response(
                    ServiceEnvironmentDailyCostsSerializer(costs).data
                )
            elif group_by == 'month':
                return Response(
                    ServiceEnvironmentMonthlyCostsSerializer(costs).data
                )
        return Response(deserializer.errors, status=400)

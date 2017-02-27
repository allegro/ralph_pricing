# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from copy import deepcopy

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from ralph_scrooge.models import (
    BaseUsage,
    CostDateStatus,
    DailyCost,
    Service,
    ServiceEnvironment,
    UsageType,
)
from ralph_scrooge.rest_api.public.auth import IsServiceOwner
from ralph_scrooge.utils.cache import memoize

USAGE_COST_NUM_DIGITS = 2
USAGE_VALUE_NUM_DIGITS = 5
GROUP_BY_CHOICES = (
    ('day', 'day'),
    ('month', 'month'),
)


@memoize
def get_valid_types():
    """We are interested here in all types except "SU" which is "Service usage
    type" (see TYPE_CHOICES in ralph_scrooge.models.usage).
    """
    return BaseUsage.objects.exclude(
        pk__in=UsageType.objects.filter(usage_type='SU')
    )


class ServiceEnvironmentCostsDeserializer(Serializer):
    service_uid = serializers.CharField()
    environment = serializers.CharField(required=False)
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    group_by = serializers.ChoiceField(choices=GROUP_BY_CHOICES)
    accepted_only = serializers.BooleanField(default=True, required=False)
    # TODO(xor-xor): Consider some less generic name for this field (it's not
    # not that easy, though, because neither `usage_types` nor `base_usages`
    # fit here in 100%).
    types = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    forecast = serializers.BooleanField(default=False, required=False)

    def validate_types(self, types):
        valid_types = get_valid_types()
        if not types:
            return valid_types
        types_validated = []
        unknown_values = []
        for t in types:
            try:
                types_validated.append(valid_types.get(symbol=t))
            except BaseUsage.DoesNotExist:
                unknown_values.append(t)
        if unknown_values:
            err = (
                'Unknown value(s): {}.'.format(
                    ', '.join(['"{}"'.format(v) for v in unknown_values]),
                )
            )
            raise serializers.ValidationError(err)
        return types_validated

    def validate(self, attrs):
        errors = []

        # Validate correctness of date range.
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        if date_from > date_to:
            errors.append("'date_from' should be less or equal to 'date_to'")

        service_uid = attrs.get('service_uid')
        env = attrs.get('environment')
        if not env:
            # Validate only service name (when `environment` field is not
            # given, all environments associated with given service are taken
            # into account).
            try:
                service = Service.objects.get(ci_uid=service_uid)
            except Service.DoesNotExist:
                errors.append(
                    'service with UID "{}" does not exist'.format(service_uid)
                )
            else:
                attrs['_service'] = service
        else:
            # Validate service environment (given indirectly by service_uid
            # and environment).
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

        # Since `types` field is not required, but we want some default values
        # in case it's not provided, we have to do that here (`validate_types`
        # will only catch `types == []` case, but not the one where this field
        # is completely omitted).
        if attrs.get('types') is None:
            attrs['types'] = get_valid_types()

        if errors:
            err_msg = '{}.'.format('; '.join(errors))
            raise serializers.ValidationError(err_msg)
        return attrs


class CostAndUsageValueSerializer(Serializer):
    cost = serializers.FloatField()
    usage_value = serializers.FloatField()
    type = serializers.CharField()


class CostWithSubcostsSerializer(CostAndUsageValueSerializer):
    subcosts = serializers.DictField(
        child=CostAndUsageValueSerializer(),
        required=False
    )


# Since we assume that maximum nesting depth for subcosts is 1, we don't need
# a truly recursive structure for `costs` field - hence this
# CostWithSubcostsSerializer / CostAndUsageValueSerializer hierarchy (instead
# of one, recursive field, which is not available out-of-the-box in DjRF
# anyway).
class CostsSerializer(Serializer):
    total_cost = serializers.FloatField()
    costs = serializers.DictField(child=CostWithSubcostsSerializer())


class DailyCostsSerializer(CostsSerializer):
    grouped_date = serializers.DateField()


class MonthlyCostsSerializer(CostsSerializer):
    grouped_date = serializers.DateField(format='%Y-%m')


class ServiceEnvironmentDailyCostsSerializer(Serializer):
    service_environment_costs = DailyCostsSerializer(many=True)


class ServiceEnvironmentMonthlyCostsSerializer(Serializer):
    service_environment_costs = MonthlyCostsSerializer(many=True)


def date_range(start, stop, step=datetime.timedelta(days=1)):
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


def _get_total_costs(qs, date_selector):
    """Sums `cost` fields by time period given as `date_selector` (i.e. "day",
    "month"), in queryset given as `qs`.

    Please note that "other" costs (i.e. not associated with those that are
    selected explicitly via `type` field in HTTP request) are also taken into
    account here (hence name "total costs")!
    """
    total_costs = {}
    results = qs.filter(depth=0).values(date_selector).annotate(
        Sum('cost')
    ).order_by(date_selector)
    for r in results:
        total_costs[r[date_selector]] = r['cost__sum']
    return total_costs


def _round_recursive(usages_and_costs):
    """Performs rounding of values in `cost` and `usage_value` fields. And
    because `usages_and_costs` dict can be actually a tree (costs having
    subcosts), it does that in a recursive manner.
    """
    rounded = {}
    if usages_and_costs is not None:
        for k, v in usages_and_costs.iteritems():
            rounded[k] = v
            rounded[k].update({
                'cost': round_safe(v['cost'], USAGE_COST_NUM_DIGITS),
                'usage_value': round_safe(
                    v['usage_value'], USAGE_VALUE_NUM_DIGITS
                ),
            })
            subcosts = v.get('subcosts')
            if subcosts is not None:
                rounded[k]['subcosts'] = _round_recursive(subcosts)
    return rounded


def fetch_costs(
        service_env,
        service,
        types,
        date_from,
        date_to,
        group_by,
        accepted_only=False,
        forecast=False,
):
    """Fetch DailyCosts associated with given `service_env` and `types`,
    in range defined by `date_from` and `date_to`, and summarize them (i.e.
    their `value` and `cost` fields) per period given by `group_by` (e.g.
    "day" or "month").

    If `service_env` is None, then `service` is used instead, which effectively
    equals to taking into account *all* environments associated with `service`.

    The result of such single summarization looks like this:

        {
            "grouped_date": datetime.date(2016, 10, 1)
            "total_cost": 1400.00,
            "costs": {
                "some_type1": {
                    "cost": 50.00,
                    "usage_value": 10.00,
                    "subcosts": {}
                },
                "some_type2": {
                    "cost": 300.0,
                    "usage_value": 0.0
                    "subcosts": {
                        # we assume that only one level of nesting is possible
                        # here (i.e., that there are no sub-subcosts)
                        "some_type3": {
                            "cost": 100.00,
                            "usage_value": 10.00
                        },
                        "some_type4": {
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
    dict is returned as a final result:

    {
        "service_environment_costs":
        [
            { <summarization for day/month 1> },
            { <summarization for day/month 2> },
            ...
        ]
    }

    And while the aforementioned costs are summarized only for selected usage
    types, the value in `total_cost` field contains sum of costs associated
    with *all* usage types for a given service environment / date range
    combination - so if there are no such "other" costs, this value should be
    equal to the sum of `cost` fields above.

    Setting `accepted_only` param to False will fetch costs that are not
    accepted. Please note that it's not possible to mix accepted and not
    accepted costs in a single request.

    The `forecast` param, when set to True will cause fetching of costs which
    were saved as "forecasted" (in contrast to "normal" ones).

    It is also worth mentioning, that precision of fields `total_cost`, `cost`
    and `usage_values` is controlled by `USAGE_COST_NUM_DIGITS` and
    `USAGE_VALUE_NUM_DIGITS` defined in this module.
    """
    date_range_query_params = {
        'date__gte': date_from,
        'date__lte': date_to,
    }
    if accepted_only and forecast:
        date_range_query_params['forecast_accepted'] = True
    elif accepted_only:
        date_range_query_params['accepted'] = True
    filtered_dates = CostDateStatus.objects.filter(
        **date_range_query_params
    ).values_list('date', flat=True)

    query_params = {
        'date__in': filtered_dates,
        'depth__lte': 1,
        'forecast': forecast,
    }
    if service_env:
        query_params['service_environment'] = service_env
    elif service:
        query_params['service_environment__service'] = service
    else:
        # This shouldn't happen.
        return {'service_environment_costs': []}
    initial_qs = DailyCost.objects_tree.filter(**query_params)

    if group_by == 'month':
        selector = 'month'
        initial_qs = initial_qs.annotate(month=TruncMonth('date'))
    else:
        selector = 'date'

    total_costs = _get_total_costs(initial_qs, selector)

    aggregated_costs = initial_qs.values(
        selector, 'path', 'type__symbol', 'type__name'
    ).annotate(
        cost_sum=Sum('cost'), value_sum=Sum('value')
    )

    # Post-process aggregated costs, as they are in form of "raw", flat
    # records from DB, but in reality, costs and subcosts are trees, so we need
    # to restore this hierarchy here. We decided to go this way (i.e., make a
    # single, "general" query and then post-process it in Python), because
    # otherwise, re-creating such tree structure would require at least a
    # couple of separate queries, which would have negative impact on
    # performance.
    cost_trees = _create_trees(aggregated_costs, selector)
    cost_trees_ = _replace_path_with_type_symbol(cost_trees)
    cost_trees_filtered = _filter_by_types(cost_trees_, types)

    # Assembly the final result (i.e., the dict that will be returned as JSON).
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
        delta = datetime.timedelta(days=1)
        date_range_ = date_range(
            date_from,
            date_to + delta,
            step=delta
        )
    for date_ in date_range_:
        total_cost_for_date = total_costs.get(
            date_,
            # None, when costs for particular date were not accepted (if
            # accepted costs were requested) otherwise 0, which means, that
            # costs for particular date were accepted, but this service-env
            # does not have any costs then
            # TODO(mkurek): consider accepting only part of the month
            # (currently only first day of month is checked when grouping by
            # month - see if above - only first day of each month is placed in
            # date_range_ )
            0 if date_ in filtered_dates else None
        )
        costs_for_date = {
            'grouped_date': date_,
            'total_cost': round_safe(
                total_cost_for_date, USAGE_COST_NUM_DIGITS
            ),
            'costs': _round_recursive(cost_trees_filtered.get(date_, {})),
        }
        final_result['service_environment_costs'].append(costs_for_date)
    return final_result


def _create_trees(aggregated_costs, date_selector):
    """From `aggregated_costs`, where each record (`ac`) has the following
    (flat) structure:

    date (as `date` or `month` - depending on `date_selector`, which may be
        "day" or "month" - in the former case it will be `date`, and `month`
        in the latter), e.g. datetime.datetime(2016, 10, 7, 0, 0)
    path (as `path`), e.g. '484/483'
    base usage type symbol (as `type__symbol`), e.g. 'subtype2'
    cost (as `cost_sum`), e.g. Decimal('222.00')
    usage value (as `value_sum`), e.g. 2.0

    ...create a dict `cost_trees`, where each entry is a tree with the
    following form:

    datetime.date(2016, 10, 7): {
        '484': {
            '_type_symbol': 'type1',
            'cost': Decimal('333.00'),
            'usage_value': 0.0,
            'type': 'Type 1',
            'subcosts': {  #  subcosts are optional
                '484/482': {
                    '_type_symbol': 'subtype1',
                    'cost': Decimal('111.00'),
                    'usage_value': 1.0,
                    'type': 'Subtype 1'
                },
                '484/483': {
                    '_type_symbol': 'subtype2',
                    'cost': Decimal('222.00'),
                    'usage_value': 2.0,
                    'type': 'Subtype 2'
                }
            }
        }
    }

    The pairing between costs and subcosts is done via the `path` component
    (e.g. a cost with '484/483' is a subcost of '484').
    """
    cost_trees = {}
    # We need to process all parent costs before processing any subcosts -
    # hence order by `depth` here.
    for ac in aggregated_costs.order_by('depth'):
        date_ = ac[date_selector]
        d = {
            ac['path']: {
                # `_type_symbol` is just a temporary key, that is removed later
                # in the process, so anyone dealing with this code shouldn't
                # rely on it (hence it starts with `_`).
                '_type_symbol': ac['type__symbol'],
                'cost': ac['cost_sum'],
                'usage_value': ac['value_sum'],
                'type': ac['type__name'],
            }
        }
        if "/" in ac['path']:
            parent = ac['path'].split("/")[0]
            if cost_trees[date_].get(parent) is None:
                cost_trees[date_][parent] = {'subcosts': d}
            else:
                if cost_trees[date_][parent].get('subcosts') is None:
                    cost_trees[date_][parent]['subcosts'] = d
                else:
                    cost_trees[date_][parent]['subcosts'].update(d)
        else:
            d[ac['path']].update({'subcosts': {}})
            if cost_trees.get(date_) is None:
                cost_trees[date_] = d
            else:
                cost_trees[date_].update(d)
    return cost_trees


def _replace_path_with_type_symbol(cost_trees):
    """Having a dict with cost trees (for the description of its structure
    see `_create_trees` function`), replace `path` components (e.g. '484',
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
                d = {type_symbol: _replace_path_with_type_symbol(vv)}
                if cost_trees_.get(k) is not None:
                    cost_trees_[k].update(d)
                else:
                    cost_trees_[k] = d
        else:
            tmp_dict[k] = v
    cost_trees_.update(tmp_dict)
    return cost_trees_


def _filter_by_types(cost_trees, types):
    """Makes a copy of `cost_trees` and filters out top-level costs from it
    if their types are not in `types`.
    """
    cost_trees_ = deepcopy(cost_trees)
    types_ = [t.symbol for t in types]
    for date_, parent_cost in cost_trees_.iteritems():
        for type_ in parent_cost.keys():
            if type_ not in types_:
                del parent_cost[type_]
    return cost_trees_


class ServiceEnvironmentCosts(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsServiceOwner)

    def post(self, request, *args, **kwargs):
        deserializer = ServiceEnvironmentCostsDeserializer(data=request.data)
        if deserializer.is_valid():
            service_env = deserializer.validated_data.get('_service_environment')  # noqa: E501
            service = deserializer.validated_data.get('_service')
            types = deserializer.validated_data['types']
            date_from = deserializer.validated_data['date_from']
            date_to = deserializer.validated_data['date_to']
            group_by = deserializer.validated_data['group_by']
            accepted_only = deserializer.validated_data['accepted_only']
            forecast = deserializer.validated_data['forecast']

            costs = fetch_costs(
                service_env,
                service,
                types,
                date_from,
                date_to,
                group_by,
                accepted_only,
                forecast,
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

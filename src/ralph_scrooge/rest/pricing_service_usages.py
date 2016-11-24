# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from ralph_scrooge.models import (
    PRICING_OBJECT_TYPES,
    DailyUsage,
    PricingObject,
    PricingService,
    Service,
    ServiceEnvironment,
    UsageType,
)
from ralph_scrooge.rest.auth import TastyPieLikeTokenAuthentication

logger = logging.getLogger(__name__)

# special object for ignoring rows with unknown pricing object when
# `ignore_unknown_services` is set to true
IGNORE_USAGE_PRICING_OBJECT = object()


# TODO(xor-xor): Consider some better naming for dicts in this hierarchy:
# pricing_service_usage -> usages -> usage
# (especially for usages).

# TODO(xor-xor) Consider separate endpoints for usages associated with:
# * service + environment
# * service_id + environment
# * service_uid + environment
# * pricing_object
# instead of a "polymorphic" one

# TODO(xor-xor): Consider json-schema based approach instead of all of those
# nested serializers, see:
# https://richardtier.com/2014/03/24/json-schema-validation-with-django-rest-framework/  # noqa

# TODO(xor-xor): Consider moving *all* exceptions used by Scrooge into a single
# module.
class ServiceEnvironmentDoesNotExistError(Exception):
    pass


class MultipleServiceEnvironmentsReturned(Exception):
    pass


def new_usage(symbol=None, value=None, remarks=None):
    return {
        'symbol': symbol,
        'value': value,
        'remarks': remarks,
    }


class UsageSerializer(Serializer):
    symbol = serializers.CharField()
    value = serializers.FloatField()
    remarks = serializers.CharField()


class UsageDeserializer(UsageSerializer):
    symbol = serializers.CharField(required=True)
    value = serializers.FloatField(required=True)
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate_symbol(self, value):
        if not UsageType.objects.filter(symbol=value).exists():
            err = (
                'usage type for symbol "{}" does not exist'
                .format(value)
            )
            raise serializers.ValidationError(err)
        return value


def new_usages(
        service=None,
        service_id=None,
        service_uid=None,
        environment=None,
        pricing_object=None,
        usages=None,
):
    return {
        'service': service,
        'service_id': service_id,
        'service_uid': service_uid,
        'environment': environment,
        'pricing_object': pricing_object,
        'usages': usages or [],
    }


class UsagesSerializer(Serializer):
    service = serializers.CharField()
    service_id = serializers.IntegerField()
    service_uid = serializers.CharField()
    environment = serializers.CharField()
    pricing_object = serializers.CharField()
    usages = UsageSerializer(many=True)


class UsagesDeserializer(UsagesSerializer):
    service = serializers.CharField(required=False)
    service_id = serializers.IntegerField(required=False)
    service_uid = serializers.CharField(required=False)
    environment = serializers.CharField(required=False)
    pricing_object = serializers.CharField(required=False)
    usages = UsageDeserializer(many=True, required=True)

    def validate_usages(self, value):
        if value is None or len(value) == 0:
            raise serializers.ValidationError("This field cannot be empty.")
        return value

    def validate_pricing_object(self, value):
        pricing_object_name = value
        if pricing_object_name is not None:
            try:
                value = PricingObject.objects.get(
                    name=pricing_object_name
                )
            except PricingObject.DoesNotExist:
                msg = (
                    "pricing_object {} does not exist".format(
                        pricing_object_name
                    )
                )
                raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        pricing_obj = attrs.get('pricing_object')
        service = attrs.get('service')
        service_id = attrs.get('service_id')
        service_uid = attrs.get('service_uid')
        env = attrs.get('environment')
        err = None
        # check for the invalid combinations of fields
        if pricing_obj and any((service, service_id, service_uid, env)):
            err = (
                "pricing_object shouldn't be used with any of: service, "
                "service_id, service_uid, environment"
            )
        elif service and any((service_id, service_uid)):
            err = (
                "service shouldn't be used with any of: service_id, "
                "service_uid"
            )
        elif service_id and service_uid:
            err = "service_id shouldn't be used with service_uid"
        elif env and not any((service, service_id, service_uid)):
            err = (
                "environment requires service or service_id or service_uid"
            )
        if err is not None:
            msg = "Invalid combination of fields: {}.".format(err)
            raise serializers.ValidationError(msg)

        # If we don't have pricing_object now, we can get it indirectly by
        # fetching proper service environment and then dummy pricing object
        # that is associated with it.
        if pricing_obj is None:
            err = None
            try:
                service_env = self._get_service_env(attrs)
            except ServiceEnvironmentDoesNotExistError as e:
                err = (
                    "service environment does not exist ({})".format(e.message)
                )
            except MultipleServiceEnvironmentsReturned as e:
                err = (
                    "multiple service environments returned, while there "
                    "should be only one ({})".format(e.message)
                )
            else:
                attrs['pricing_object'] = service_env.dummy_pricing_object
            if err is not None:
                if self.root.initial_data.get('ignore_unknown_services'):
                    attrs['pricing_object'] = IGNORE_USAGE_PRICING_OBJECT
                    attrs['_ignore_error'] = err
                else:
                    raise serializers.ValidationError(err)

        return attrs

    def _get_service_env(self, attrs):
        """Fetch ServiceEnvironment basing on the attrs (environment name
        + serivce ID/UID/name) from the incoming request. Since our API allows
        specifying service by its ID, UID or name, these variants are checked
        in that order.
        """
        se_params = {
            'environment__name': attrs.get('environment'),
        }
        if attrs.get('service_id'):
            se_params['service_id'] = attrs['service_id']
        elif attrs.get('service_uid'):
            se_params['service__ci_uid'] = attrs['service_uid']
        else:
            se_params['service__name'] = attrs['service']
        try:
            se = ServiceEnvironment.objects.get(**se_params)
        except ServiceEnvironment.DoesNotExist:
            params = ", ".join(
                ["{}={}".format(k, v) for k, v in se_params.items()]
            )
            raise ServiceEnvironmentDoesNotExistError(
                'query params: {}'.format(params)
            )
        except ServiceEnvironment.MultipleObjectsReturned:
            params = ", ".join(
                ["{}={}".format(k, v) for k, v in se_params.items()]
            )
            raise MultipleServiceEnvironmentsReturned(
                'query params: {}'.format(params)
            )
        return se


def new_pricing_service_usage(
        pricing_service=None,
        pricing_service_id=None,
        usages=None,
        date=None,
        overwrite='no',
):
    return {
        'pricing_service': pricing_service,
        'pricing_service_id': pricing_service_id,
        'usages': usages or [],
        'date': date,
        'overwrite': overwrite,
    }


class PricingServiceUsageSerializer(Serializer):
    pricing_service = serializers.CharField()
    pricing_service_id = serializers.IntegerField()
    date = serializers.DateField()
    usages = UsagesSerializer(many=True)


class PricingServiceUsageDeserializer(PricingServiceUsageSerializer):
    pricing_service_id = serializers.IntegerField(required=False)
    overwrite = serializers.CharField(required=False, default='no')
    ignore_unknown_services = serializers.BooleanField(
        required=False, default=False
    )
    usages = UsagesDeserializer(many=True, required=True)

    def validate_usages(self, value):
        if value is None or len(value) == 0:
            raise serializers.ValidationError("This field cannot be empty.")
        return value

    def validate_overwrite(self, value):
        if value not in ('no', 'delete_all_previous', 'values_only'):
            raise serializers.ValidationError(
                "Invalid value: {}".format(value)
            )
        return value

    def validate_pricing_service(self, value):
        try:
            PricingService.objects.get(name=value)
        except PricingService.DoesNotExist:
            raise serializers.ValidationError(
                "Unknown service name: {}".format(value)
            )
        return value


@api_view(['GET'])
@authentication_classes((TastyPieLikeTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def list_pricing_service_usages(
        request, usages_date, pricing_service_id, *args, **kwargs
):
    err_msg = None
    service = None
    try:
        pricing_service = PricingService.objects.get(id=pricing_service_id)
    except PricingService.DoesNotExist:
        err_msg = (
            "Pricing Service with ID {} does not exist."
            .format(pricing_service_id)
        )

    service_id = request.GET.get('service_id')
    if service_id:
        try:
            service = Service.objects.get(id=service_id)
        except ObjectDoesNotExist:
            err_msg = (
                "Service with ID {} does not exist."
                .format(service_id)
            )

    # We can't catch invalid dates like '2016-09-33' in URL patterns, so we
    # have to do that here.
    try:
        datetime.strptime(usages_date, '%Y-%m-%d')
    except ValueError:
        err_msg = (
            '"{}" has the correct format, but is an invalid date.'
            .format(usages_date)
        )

    if err_msg is not None:
        return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    usages = get_usages(usages_date, pricing_service, service)
    return Response(PricingServiceUsageSerializer(usages).data)


def get_usages(usages_date, pricing_service, service=None):
    """Create pricing service usage dict (i.e. the most "outer" one when
    looking at the JSON returned with the HTTP response), and fill it with
    the usages by going through these steps:
    1) For every usage type associated with given pricing service, fetch
       daily usages for a given date (`usages_date`) and store them in a dict
       keyed by daily pricing object, where the value is a list of tulpes
       (symbol, value, remarks) designating the actual usages (i.e. the most
       "inner" ones).
    2) By iterating over the structure from the previous step, wrap the "inner"
       usages into a structure containing the information re: the service and
       environment (or the pricing object).
    3) The list dicts from the previous step are finally added into a top-level
       (the most "outer" one) dict, under the "usages" key.
    """
    ps = new_pricing_service_usage(
        pricing_service=pricing_service.name,
        pricing_service_id=pricing_service.id,
        date=usages_date,
    )
    usages_dict = defaultdict(list)

    for usage_type in pricing_service.get_usage_types_for_date(usages_date):
        _kwargs_filter = {'date': usages_date}
        if service:
            _kwargs_filter['service_environment__service'] = service
        daily_usages = usage_type.dailyusage_set.filter(
            **_kwargs_filter
        ).select_related(
            'service_environment',
            'service_environment__service',
            'service_environment__environment',
            'daily_pricing_object'
        )
        for daily_usage in daily_usages:
            usages_dict[daily_usage.daily_pricing_object].append(
                (
                    daily_usage.type.symbol,
                    daily_usage.value,
                    daily_usage.remarks
                )
            )

    for dpo, uu in usages_dict.iteritems():
        se = dpo.service_environment
        usages = new_usages(
            service=se.service.name,
            service_id=se.service.id,
            service_uid=se.service.ci_uid,
            environment=se.environment.name,
        )
        if dpo.pricing_object != PRICING_OBJECT_TYPES.DUMMY:
            usages['pricing_object'] = dpo.pricing_object.name
        usages['usages'] = [
            new_usage(symbol=u[0], value=u[1], remarks=u[2]) for u in uu
        ]
        ps['usages'].append(usages)
    return ps


@api_view(['POST'])
@authentication_classes((TastyPieLikeTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def create_pricing_service_usages(request, *args, **kwargs):
    deserializer = PricingServiceUsageDeserializer(data=request.data)
    if deserializer.is_valid():
        save_usages(deserializer.validated_data)
        return HttpResponse(status=201)
    return Response(deserializer.errors, status=400)


@transaction.atomic
def save_usages(pricing_service_usage):
    """This combines three "low-level" steps:
    1) The transformation of the incoming pricing_service_usage dict into
       a data structure needed by next two steps.
    2) Removing previous usages associated with a given day.
    3) The actual save of the incoming usages.
    """
    logger.info("Saving usages for service {}".format(
        pricing_service_usage['pricing_service']
    ))
    daily_usages, usages_daily_pricing_objects = get_usages_for_save(
        pricing_service_usage
    )
    remove_previous_daily_usages(
        pricing_service_usage['overwrite'],
        pricing_service_usage['date'],
        usages_daily_pricing_objects,
    )
    DailyUsage.objects.bulk_create(daily_usages)


def get_usages_for_save(pricing_service_usage):
    """This function transforms incoming pricing_service_usage dict into a
    tuple, where the first element is a list containing DailyUsage object(s),
    and the second is a dict keyed by UsageType, where the value is a list
    of DailyPricingObject(s)

    Only the first element of this tuple is actually used for saving usages to
    database - the second one is needed for removing previous daily usages for
    a given day (see `remove_previous_daily_usages` function`).
    """
    usage_types_cache = {}
    daily_usages = []
    usages_daily_pricing_objects = defaultdict(list)

    for usages in pricing_service_usage['usages']:
        for usage in usages['usages']:
            try:
                usage_type = usage_types_cache[usage['symbol']]
            except KeyError:
                usage_type = UsageType.objects.get(symbol=usage['symbol'])
            usage_types_cache[usage['symbol']] = usage_type
            if usages['pricing_object'] is IGNORE_USAGE_PRICING_OBJECT:
                logger.warning(
                    'Ignoring usages for pricing service {}: {}'.format(
                        pricing_service_usage['pricing_service'],
                        usages['_ignore_error']
                    )
                )
                continue
            daily_pricing_object = (
                usages['pricing_object'].get_daily_pricing_object(
                    pricing_service_usage['date']
                )
            )
            daily_usage = DailyUsage(
                date=pricing_service_usage['date'],
                type=usage_type,
                value=usage['value'],
                daily_pricing_object=daily_pricing_object,
                service_environment=(
                    daily_pricing_object.service_environment
                ),
                remarks=usage.get('remarks', ''),
            )
            daily_usages.append(daily_usage)
            usages_daily_pricing_objects[usage_type].append(
                daily_pricing_object
            )
    return (daily_usages, usages_daily_pricing_objects)


def remove_previous_daily_usages(overwrite, date, usages_dp_objs):
    """Handler for 'overwrite' option that can be added to the incoming data.
    For detailed description (with examples) of what this option does, see the
    docs for our REST API. Please note, that 'no' variant is deliberately
    ignored here, because that's default behavior.
    """
    if overwrite in ('values_only', 'delete_all_previous'):
        logger.debug('Remove previous values ({})'.format(overwrite))
        for ut, dp_objs in usages_dp_objs.iteritems():
            previous_usages = DailyUsage.objects.filter(date=date, type=ut)
            if overwrite == 'values_only':
                previous_usages = previous_usages.filter(
                    daily_pricing_object__in=dp_objs
                )
            previous_usages.delete()

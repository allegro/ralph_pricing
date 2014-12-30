# -*- coding: utf-8 -*-
"""
ReST API for Scrooge
------------------------------------

Done with TastyPie and Django Rest Framework.

Scrooge API provide endpoint for services to push usages of their resources
by services / pricing objects.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from collections import defaultdict

import django_filters
from django.conf.urls.defaults import url
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from tastypie import http, fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import Resource
from tastypie.exceptions import ImmediateHttpResponse

from ralph_scrooge.models import (
    DailyUsage,
    PricingObject,
    PricingService,
    ServiceEnvironment,
    SyncStatus,
    UsageType,
)


logger = logging.getLogger(__name__)


# =============================================================================
# SERVICES USAGES PUSH API
# =============================================================================
class UsageObject(object):
    """
    Single usage of usage type
    """
    symbol = None
    value = None

    def __init__(self, symbol=None, value=None, **kwargs):
        self.symbol = symbol
        self.value = value

    def to_dict(self, exclude_empty=False):
        return {
            'symbol': self.symbol,
            'value': self.value,
        }


class UsagesObject(object):
    """
    Container for service or pricing object usages
    """
    service = None
    service_id = None
    environment = None
    pricing_object = None
    usages = []  # list of UsageObject

    def __init__(
        self,
        service=None,
        service_id=None,
        environment=None,
        pricing_object=None,
        usages=None,
        **kwargs
    ):
        self.service = service
        self.service_id = service_id
        self.environment = environment
        self.pricing_object = pricing_object
        self.usages = usages or []

    def to_dict(self, exclude_empty=False):
        data = {
            'usages': [u.to_dict(exclude_empty) for u in self.usages],
        }
        for f in ('service', 'service_id', 'environment', 'pricing_object'):
            v = getattr(self, f)
            if (exclude_empty and v) or not exclude_empty:
                data[f] = v
        return data


class PricingServiceUsageObject(object):
    """
    Container for pricing service resources usages per service
    """
    pricing_service = None
    pricing_service_id = None
    date = None
    overwrite = None
    usages = []  # list of UsagesObject

    def __init__(
        self,
        pricing_service=None,
        pricing_service_id=None,
        usages=None,
        date=None,
        **kwargs
    ):
        self.pricing_service = pricing_service
        self.pricing_service_id = pricing_service_id
        self.date = date
        self.usages = usages or []
        self.overwrite = 'no'  # default overwrite

    def to_dict(self, exclude_empty=False):
        result = {
            'date': self.date,
            'pricing_service': self.pricing_service,
            'pricing_service_id': self.pricing_service_id,
            'overwrite': self.overwrite,
            'usages': [u.to_dict(exclude_empty) for u in self.usages]
        }
        return result


# Tastypie resources
class UsageResource(Resource):
    symbol = fields.CharField(attribute='symbol')
    value = fields.FloatField(attribute='value')

    class Meta:
        object_class = UsageObject


class UsagesResource(Resource):
    service = fields.CharField(attribute='service', null=True)  # name
    service_id = fields.CharField(attribute='service_id', null=True)  # id
    environment = fields.CharField(attribute='environment', null=True)  # name
    pricing_object = fields.CharField(attribute='pricing_object', null=True)
    usages = fields.ToManyField(UsageResource, 'usages', null=True)

    class Meta:
        object_class = UsagesObject

    def hydrate_usages(self, bundle):
        # need to use hydrate_m2m due to limitations of tastypie in dealing
        # with fields.ToManyField hydration
        usages_bundles = self.usages.hydrate_m2m(bundle)
        bundle.obj.usages = [ub.obj for ub in usages_bundles]
        return bundle


class PricingServiceUsageResource(Resource):
    """
    Provides PUSH REST API for services. Each service can use this API to post
    information about usage of service resources by services.

    This endpoint supports only POST HTTP method. API format is as follows:
    {
        "pricing_service": "<service name or id>",
        "date": "<date>",
        "overwrite: "no|values_only|delete_all_previous",
        "usages": [
            {
                "service": "<service name or id>",
                "pricing_object": "<pricing_object_name>",
                "usages": [
                    {
                        "symbol": "<usage_type_1_symbol>",
                        "value": <usage1>
                    },
                ...
                ]
            },
            ...
        ]
    }

    Usage symbol is symbol defined in Scrooge models.

    Example:
    {
        "pricing_service": "pricing_service1",
        "date": "2013-10-10",
        "usages": [
            {
                "service": "service1",
                "environment": "env1",
                "usages": [
                    {
                        "symbol": "requests",
                        "value": 123
                    },
                    {
                        "symbol": "transfer",
                        "value": 321
                    }
                ]
            },
            {
                "pricing_object": "pricing_object1",
                "usages": [
                    {
                        "symbol": "requests",
                        "value": 543
                    },
                    {
                        "symbol": "transfer",
                        "value": 565
                    }
                ]
            },
            {
                "service_id": 123,
                "environment": "env2",
                "usages": [
                    {
                        "symbol": "requests",
                        "value": 788
                    },
                    {
                        "symbol": "transfer",
                        "value": 234
                    }
                ]
            }
        ]
    }

    Possible return HTTP codes:
    201 - everything ok.
    400 - invalid symbol or name (pricing service, usage, service, environment,
          pricing object).
    401 - authentication/authorization error.
    500 - error during parsing request/data.
    """
    pricing_service = fields.CharField(attribute='pricing_service')
    date = fields.DateField(attribute='date')
    overwrite = fields.CharField(attribute='overwrite')
    usages = fields.ToManyField(
        UsagesResource,
        'usages',
        full=True,
    )

    class Meta:
        list_allowed_methos = ['post']
        resource_name = 'pricingserviceusages'
        authentication = ApiKeyAuthentication()
        object_class = PricingServiceUsageObject
        include_resource_uri = False

    # =================
    # POST
    # =================
    def obj_create(self, bundle, request=None, **kwargs):
        """
        POST API (creates daily usages)
        """
        bundle.obj = PricingServiceUsageObject()
        try:
            bundle = self.full_hydrate(bundle)
            self.save_usages(bundle.obj)
        except Exception:
            logger.exception(
                "Exception occured while saving usages (service: {0})".format(
                    bundle.obj.pricing_service
                )
            )
            raise
        return bundle

    def detail_uri_kwargs(self, bundle_or_obj):
        return {}

    def hydrate_usages(self, bundle):
        """
        Hydrate usages for PUSH API (data to object)
        """
        # need to use hydrate_m2m due to limitations of tastypie in dealing
        # with fields.ToManyField hydration
        usages_bundles = self.usages.hydrate_m2m(bundle)
        # save usages per service / pricing object in bundle object
        bundle.obj.usages = [vub.obj for vub in usages_bundles]
        return bundle

    @classmethod
    def save_usages(cls, pricing_service_usages):
        """
        Save usages of service resources per service

        If any error occur during parsing service usages, no usage is saved
        and Bad Request response is returned.
        """
        usage_types = {}
        daily_usages = []

        # check if service exists
        ps_params = {}
        if pricing_service_usages.pricing_service_id:
            ps_params['id'] = pricing_service_usages.pricing_service_id
        elif pricing_service_usages.pricing_service:
            ps_params['name'] = pricing_service_usages.pricing_service
        try:
            PricingService.objects.get(**ps_params)
        except PricingService.DoesNotExist:
            raise ImmediateHttpResponse(response=http.HttpBadRequest(
                "Invalid pricing service name ({}) or id ({})".format(
                    pricing_service_usages.pricing_service,
                    pricing_service_usages.pricing_service_id,
                )
            ))

        # check if date is properly set
        assert isinstance(pricing_service_usages.date, datetime.date)
        # check if overwrite is properly set
        assert pricing_service_usages.overwrite in (
            'no',
            'delete_all_previous',
            'values_only',
        )
        usages_daily_pricing_objects = defaultdict(list)
        for usages in pricing_service_usages.usages:
            try:
                pricing_object = None
                if usages.pricing_object:
                    pricing_object = PricingObject.objects.get(
                        name=usages.pricing_object,
                    )
                elif usages.service_id and usages.environment:
                    service_environment = ServiceEnvironment.objects.get(
                        service__id=usages.service_id,
                        environment__name=usages.environment,
                    )
                    pricing_object = service_environment.dummy_pricing_object
                elif usages.service and usages.environment:
                    service_environment = ServiceEnvironment.objects.get(
                        service__name=usages.service,
                        environment__name=usages.environment,
                    )
                    pricing_object = service_environment.dummy_pricing_object
                else:
                    raise ImmediateHttpResponse(response=http.HttpBadRequest((
                        "Pricing Object (Host, IP etc) or Service and "
                        "Environment has to be provided"
                    )))

                for usage in usages.usages:
                    try:
                        usage_type = usage_types.get(
                            usage.symbol,
                            UsageType.objects.get(symbol=usage.symbol)
                        )
                        daily_pricing_object = (
                            pricing_object.get_daily_pricing_object(
                                pricing_service_usages.date
                            )
                        )
                        daily_usage = DailyUsage(
                            date=pricing_service_usages.date,
                            type=usage_type,
                            value=usage.value,
                            daily_pricing_object=daily_pricing_object,
                            service_environment=(
                                daily_pricing_object.service_environment
                            ),
                        )
                        daily_usages.append(daily_usage)
                        usages_daily_pricing_objects[usage_type].append(
                            daily_pricing_object
                        )
                    except UsageType.DoesNotExist:
                        raise ImmediateHttpResponse(
                            response=http.HttpBadRequest(
                                "Invalid usage type symbol: {}".format(
                                    usage.symbol,
                                )
                            )
                        )
            except PricingObject.DoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpBadRequest(
                    "Invalid pricing object name or id ({})".format(
                        usages.pricing_object
                    )
                ))
            except ServiceEnvironment.DoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpBadRequest(
                    "Invalid service or environment name ({} / {})".format(
                        usages.service,
                        usages.environment,
                    )
                ))
        logger.info("Saving usages for service {0}".format(
            pricing_service_usages.pricing_service
        ))

        # remove previous daily usages
        if pricing_service_usages.overwrite in (
            'values_only',
            'delete_all_previous'
        ):
            logger.debug('Remove previous values ({})'.format(
                pricing_service_usages.overwrite,
            ))
            for usage_type, dpos in usages_daily_pricing_objects.iteritems():
                previuos_usages = DailyUsage.objects.filter(
                    date=pricing_service_usages.date,
                    type=usage_type,
                )
                if pricing_service_usages.overwrite == 'values_only':
                    previuos_usages = previuos_usages.filter(
                        daily_pricing_object__in=dpos
                    )
                previuos_usages.delete()

        # bulk save all usages
        DailyUsage.objects.bulk_create(daily_usages)

    # =================
    # GET
    # =================
    def obj_get(self, request=None, **kwargs):
        """
        Usages GET API
        Requires url (resource) in following format:
            <pricing_service_name>/<date(YYYY-MM-DD)>
        """
        usages_date = datetime.datetime.strptime(
            kwargs['date'],
            '%Y-%m-%d'
        ).date()
        return self._get_pricing_service_usages(
            kwargs['pricing_service_id'],
            usages_date
        )

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pricing_service_id>[\w\d\s_.-]+)/(?P<date>[\d-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),  # noqa
        ]

    def full_dehydrate(self, bundle, *args, **kwargs):
        """
        Dehydration for GET API (object to dict)
        """
        data = bundle.obj.to_dict(exclude_empty=True)
        del data['overwrite']  # remove default overwrite info from result
        return data

    @classmethod
    def _get_pricing_service_usages(cls, pricing_service_id, date):
        """
        Returns usages of pricing service (on date) for GET API
        """
        try:
            pricing_service = PricingService.objects.get(
                id=pricing_service_id,
            )
        except PricingService.DoesNotExist:
            raise ImmediateHttpResponse(response=http.HttpBadRequest(
                "Invalid pricing service id: {}".format(
                    pricing_service_id,
                )
            ))
        else:
            ps = PricingServiceUsageObject(
                pricing_service=pricing_service.name,
                date=date,
                usages=[],
            )
            usages_dict = defaultdict(list)
            # iterate through pricing service usage types
            for usage_type in pricing_service.usage_types.all():
                daily_usages = usage_type.dailyusage_set.filter(
                    date=date
                ).select_related(
                    'service_environment',
                    'service_environment__service',
                    'service_environment__environment',
                    'pricing_object'
                )
                for daily_usage in daily_usages:
                    usages_dict[daily_usage.daily_pricing_object].append(
                        (daily_usage.type.symbol, daily_usage.value)
                    )
            # save usages tp UsagesObjects
            for dpo, u in usages_dict.iteritems():
                usages = UsagesObject()
                se = dpo.service_environment
                usages.service = se.service.name
                usages.service_id = se.service.id
                usages.environment = se.environment.name
                # if pricing object is not dummy pricing object for service
                # environment use it
                if se.dummy_pricing_object != dpo.pricing_object:
                    usages.pricing_object = dpo.pricing_object.name
                usages.usages = [UsageObject(k, v) for k, v in u]
                ps.usages.append(usages)
        return ps


# =============================================================================
# SYNC STATUS API
# =============================================================================
class SyncStatusSerializer(ModelSerializer):
    class Meta:
        model = SyncStatus
        exclude = ('created', 'modified', 'id', 'cache_version')


class SyncStatusFilter(django_filters.FilterSet):
    class Meta:
        model = SyncStatus
        fields = {
            'date': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'plugin': ['exact'],
            'success': ['exact']
        }


class SyncStatusViewSet(ModelViewSet):
    queryset = SyncStatus.objects.order_by('-date')
    serializer_class = SyncStatusSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SyncStatusFilter
    resource_name = 'sync_status'

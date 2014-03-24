# -*- coding: utf-8 -*-

"""ReST API for Scrooge
   ------------------------------------

Done with TastyPie."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging

from tastypie import http, fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import Resource
from tastypie.exceptions import ImmediateHttpResponse

from ralph_pricing.models import DailyUsage, Service, Venture, UsageType


logger = logging.getLogger(__name__)


class UsageObject(object):
    symbol = None
    value = None

    def __init__(self, symbol=None, value=None, **kwargs):
        self.symbol = symbol
        self.value = value

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'value': self.value,
        }


class VentureUsageObject(object):
    venture = None
    usages = []

    def __init__(self, venture=None, usages=None, **kwargs):
        self.venture = venture
        self.usages = usages or []

    def to_dict(self):
        return {
            'venture': self.venture,
            'usages': [u.to_dict() for u in self.usages],
        }


class ServiceUsageObject(object):
    service = None
    # date = None
    venture_usages = []

    def __init__(self, service=None, venture_usages=None, date=None, **kwargs):
        self.service = service
        if date:
            self.date = date
        self.venture_usages = venture_usages or []

    def to_dict(self):
        result = {
            'service': self.service,
            'venture_usages': [vu.to_dict() for vu in self.venture_usages]
        }
        if hasattr(self, 'date'):
            result['date'] = self.date
        return result


class UsageResource(Resource):
    symbol = fields.CharField(attribute='symbol')
    value = fields.FloatField(attribute='value')

    class Meta:
        object_class = UsageObject


class VentureUsageResource(Resource):
    venture = fields.CharField(attribute='venture')
    usages = fields.ToManyField(UsageResource, 'usages')

    class Meta:
        object_class = VentureUsageObject

    def hydrate_usages(self, bundle):
        usages_bundles = self.usages.hydrate_m2m(bundle)
        bundle.obj.usages = [ub.obj for ub in usages_bundles]
        return bundle


class ServiceUsageResource(Resource):
    service = fields.CharField(attribute='service')
    date = fields.DateTimeField(default=datetime.date.today, attribute='date')
    venture_usages = fields.ToManyField(
        VentureUsageResource,
        'venture_usages',
        full=True
    )

    class Meta:
        list_allowed_methos = ['post']
        resource_name = 'serviceusages'
        authentication = ApiKeyAuthentication()
        object_class = ServiceUsageObject
        include_resource_uri = False

    @classmethod
    def save_usages(cls, service_usages):
        usage_types = {}
        daily_usages = []

        # check if service exists
        try:
            Service.objects.get(symbol=service_usages.service)
        except Service.DoesNotExist:
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest("Invalid service symbol")
            )

        for venture_usages in service_usages.venture_usages:
            venture = None
            try:
                venture = Venture.objects.get(symbol=venture_usages.venture)
                for usage in venture_usages.usages:
                    try:
                        usage_type = usage_types.get(
                            usage.symbol,
                            UsageType.objects.get(symbol=usage.symbol)
                        )
                        daily_usages.append(DailyUsage(
                            date=service_usages.date,
                            pricing_venture=venture,
                            type=usage_type,
                            value=usage.value,
                        ))
                    except UsageType.DoesNotExist:
                        raise ImmediateHttpResponse(
                            response=http.HttpBadRequest(
                                "Invalid usage type symbol"
                            )
                        )
            except Venture.DoesNotExist:
                raise ImmediateHttpResponse(
                    response=http.HttpBadRequest("Invalid venture symbol")
                )
        logger.debug(
            "Saving usages for service {0}".format(service_usages.service)
        )
        DailyUsage.objects.bulk_create(daily_usages)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = ServiceUsageObject()
        try:
            bundle = self.full_hydrate(bundle)
            self.save_usages(bundle.obj)
        except Exception:
            logger.exception(
                "Exception occured while saving usages (service: {0})".format(
                    bundle.obj.service
                )
            )
            raise
        return bundle

    def detail_uri_kwargs(self, bundle_or_obj):
        return {}

    def hydrate_venture_usages(self, bundle):
        venture_usages_bundles = self.venture_usages.hydrate_m2m(bundle)
        bundle.obj.venture_usages = [vub.obj for vub in venture_usages_bundles]
        return bundle

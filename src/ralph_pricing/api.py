# -*- coding: utf-8 -*-
"""
ReST API for Scrooge
------------------------------------

Done with TastyPie.

Scrooge API provide endpoint for services to push usages of their resources
by ventures.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from collections import defaultdict

from tastypie import http, fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import Resource
from tastypie.exceptions import ImmediateHttpResponse

from ralph_pricing.models import DailyUsage, Service, Venture, UsageType


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

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'value': self.value,
        }


class VentureUsageObject(object):
    """
    Container for venture usages
    """
    venture = None
    usages = []  # list of UsageObject

    def __init__(self, venture=None, usages=None, **kwargs):
        self.venture = venture
        self.usages = usages or []

    def to_dict(self):
        return {
            'venture': self.venture,
            'usages': [u.to_dict() for u in self.usages],
        }


class ServiceUsageObject(object):
    """
    Container for service resources usages per venture
    """
    service = None
    date = None
    overwrite = None
    venture_usages = []  # list of VentureUsageObject

    def __init__(self, service=None, venture_usages=None, date=None, **kwargs):
        self.service = service
        self.date = date
        self.venture_usages = venture_usages or []
        self.overwrite = None

    def to_dict(self):
        result = {
            'date': self.date,
            'service': self.service,
            'overwrite': self.overwrite,
            'venture_usages': [vu.to_dict() for vu in self.venture_usages]
        }
        return result


# Tastypie resources
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
        # need to use hydrate_m2m due to limitations of tastypie in dealing
        # with fields.ToManyField hydration
        usages_bundles = self.usages.hydrate_m2m(bundle)
        bundle.obj.usages = [ub.obj for ub in usages_bundles]
        return bundle


class ServiceUsageResource(Resource):
    """
    Provides PUSH REST API for services. Each service can use this API to post
    information about usage of service resources by ventures.

    This endpoint supports only POST HTTP method. API format is as follows:
    {
        "service": "<service_symbol>",
        "date": "<date>",
        "venture_usages": [
            {
                "venture": "<venture_symbol>",
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

    Service, venture and usage symbol are symbols defined in Scrooge models.

    Example:
    {
        "service": "service_symbol",
        "date": "2013-10-10",
        "venture_usages": [
            {
                "venture": "venture1",
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
                "venture": "venture2",
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
                "venture": "venture3",
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
    400 - invalid symbol (venture, usage or service).
    401 - authentication/authorization error.
    500 - error during parsing request/data.
    """
    service = fields.CharField(attribute='service')
    date = fields.DateTimeField(attribute='date')
    overwrite = fields.CharField(attribute='overwrite', default='values_only')
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
        """
        Save usages of service resources per venture

        If any error occur during parsing service usages, no usage is saved
        and Bad Request response is returned.
        """
        usage_types = {}
        daily_usages = []

        # check if service exists
        try:
            Service.objects.get(symbol=service_usages.service)
        except Service.DoesNotExist:
            raise ImmediateHttpResponse(
                response=http.HttpBadRequest("Invalid service symbol")
            )

        # check if date is properly set
        assert isinstance(
            service_usages.date,
            (datetime.date, datetime.datetime)
        )
        usages_ventures = defaultdict(list)
        for venture_usages in service_usages.venture_usages:
            try:
                venture = Venture.objects.get(
                    symbol=venture_usages.venture,
                    is_active=True,
                )
                for usage in venture_usages.usages:
                    try:
                        usage_type = usage_types.get(
                            usage.symbol,
                            UsageType.objects.get(symbol=usage.symbol)
                        )
                        usages_ventures[usage_type].append(venture)
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
                    response=http.HttpBadRequest(
                        "Invalid venture symbol or venture is inactive"
                    )
                )
        logger.error(
            "Saving usages for service {0}".format(service_usages.service)
        )

        # remove previous daily usages
        if service_usages.overwrite in ('values_only', 'delete_all_previous'):
            for usage_type, ventures in usages_ventures.iteritems():
                previuos_usages = DailyUsage.objects.filter(
                    date=service_usages.date,
                    type=usage_type,
                )
                if service_usages.overwrite == 'values_only':
                    previuos_usages = previuos_usages.filter(
                        pricing_venture__in=ventures
                    )
                previuos_usages.delete()

        # bulk save all usages
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
        # need to use hydrate_m2m due to limitations of tastypie in dealing
        # with fields.ToManyField hydration
        venture_usages_bundles = self.venture_usages.hydrate_m2m(bundle)
        # save usages per venture in bundle object
        bundle.obj.venture_usages = [vub.obj for vub in venture_usages_bundles]
        return bundle

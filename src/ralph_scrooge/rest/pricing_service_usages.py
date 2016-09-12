# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import logging
from collections import defaultdict

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from ralph_scrooge.models import (
    DailyUsage,
    PricingObject,
    PricingService,  # XXX not used..?
    ServiceEnvironment,
    UsageType,
)

logger = logging.getLogger(__name__)


class PricingServiceUsageObject(object):
    """
    Container for pricing service resources usages per service
    """
    pricing_service = None
    pricing_service_id = None  # XXX ?
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

    # def to_dict(self, exclude_empty=False):
    #     result = {
    #         'date': self.date,
    #         'pricing_service': self.pricing_service,
    #         'pricing_service_id': self.pricing_service_id,
    #         'overwrite': self.overwrite,
    #         'usages': [u.to_dict(exclude_empty) for u in self.usages]
    #     }
    #     return result


class PricingServiceUsageObjectSerializer(Serializer):
    pricing_service = None
    date = None
    overwrite = None
    usages = []  # list of UsagesObject


class PricingServiceUsages(APIView):

    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.raw_post_data)
        self.validate(post_data)
        self.save_usages(post_data)
        result = {
            'status': 'ok',
            'message': 'success!',
        }  # XXX ?
        return Response(result, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        usages_date = datetime.datetime.strptime(
            kwargs['date'],
            '%Y-%m-%d'
        ).date()
        pricing_service_id = kwargs['pricing_service_id']
        # XXX what about wrapping this into some function?
        # pricing_service = PricingService.objects_admin.get(  # XXX must be admin..?
        pricing_service = PricingService.objects.get(  # XXX must be admin..?
            id=pricing_service_id,
        )  # XXX try/except
        # ps = PricingServiceUsageObject(  # XXX
        #     pricing_service=pricing_service.name,
        #     date=usages_date,
        #     usages=[],
        # )
        ps = {
            'pricing_service': pricing_service.name,
            'date': usages_date,
            'usages': [],
        }  # XXX
        usages_dict = defaultdict(list)

        # iterate through pricing service usage types
        for usage_type in pricing_service.usage_types.all():
            daily_usages = usage_type.dailyusage_set.filter(
                date=usages_date
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
            usages = {}
            se = dpo.service_environment
            usages['service'] = se.service.name
            usages['service_id'] = se.service.id
            usages['environment'] = se.environment.name
            # if pricing object is not dummy pricing object for service
            # environment use it
            if se.dummy_pricing_object != dpo.pricing_object:
                usages['pricing_object'] = dpo.pricing_object.name
            # usages.usages = [UsageObject(k, v) for k, v in u]  # XXX
            usages['usages'] = [{'symbol': k, 'value': v} for k, v in u]  # XXX
            ps['usages'].append(usages)
            # XXX missing:
            # pricing_service_id (np. null)
            # datetime jako string
        # XXX
        ps['pricing_service_id'] = None
        ps['date'] = ps['date'].strftime('%Y-%m-%d')
        # result = json.dumps(ps)
        return Response(ps)


    def validate(self, post_data):  # XXX change name of this fn
        # check if service exists
        ps_params = {}
        if post_data.get('pricing_service_id'):
            ps_params['id'] = post_data['pricing_service_id']
        elif post_data.get('pricing_service'):
            ps_params['name'] = post_data['pricing_service']
            PricingService.objects_admin.get(**ps_params)  # XXX try/except

        # check if date is properly set
        # assert isinstance(post_data['date'], datetime.date)  # XXX

        # check if overwrite is properly set
        assert post_data.get('overwrite', 'no') in (  # XXX
            'no',
            'delete_all_previous',
            'values_only',
        )

    def get_service_env(self, usages):
        se_params = {
            'environment__name': usages.get('environment'),
        }
        if usages.service_id:
            se_params['service_id'] = usages['service_id']
        elif usages.service_uid:
            se_params['service__ci_uid'] = usages['service_uid']
        else:
            se_params['service__name'] = usages['service']
        return ServiceEnvironment.objects.get(**se_params)  # XXX try/except

    def remove_previous_daily_usages(self, overwrite, date, usages_dp_objs):
        if overwrite in ('values_only', 'delete_all_previous'):
            logger.debug('Remove previous values ({})'.format(overwrite))
            for k, v in usages_dp_objs.iteritems():
                previuos_usages = DailyUsage.objects.filter(date=date, type=k)
                if overwrite == 'values_only':
                    previuos_usages = previuos_usages.filter(
                        daily_pricing_object__in=v
                    )
                previuos_usages.delete()

    def get_pricing_object(self, usages):
        if usages.get('pricing_object'):
            pricing_object = PricingObject.objects.get(
                name=usages['pricing_object'],
            )  # XXX try/except
        else:
            if not usages.get('environment') or not any([
                usages.get('service_id'),
                usages.get('service'),
                usages.get('service_uid'),
            ]):
                pass
                # XXX raise some exception here
            else:
                service_env = self.get_service_env(usages)
                pricing_object = service_env.dummy_pricing_object  # XXX ?
        return pricing_object

    def get_usages(self, post_data):
        usage_types = {}  # XXX
        daily_usages = []
        usages_daily_pricing_objects = defaultdict(list)
        date = datetime.datetime.strptime(post_data['date'], '%Y-%m-%d').date()

        for usages in post_data['usages']:
            pricing_object = self.get_pricing_object(usages)
            for usage in usages['usages']:
                usage_type = usage_types.get(
                    usage['symbol'],
                    UsageType.objects_admin.get(symbol=usage['symbol'])  # XXX try/except
                )
                daily_pricing_object = (
                    pricing_object.get_daily_pricing_object(date)
                )
                daily_usage = DailyUsage(
                    date=date,
                    type=usage_type,
                    value=usage['value'],
                    daily_pricing_object=daily_pricing_object,
                    service_environment=(
                        daily_pricing_object.service_environment
                    ),
                )
                daily_usages.append(daily_usage)
                usages_daily_pricing_objects[usage_type].append(
                    daily_pricing_object
                )
        return (daily_usages, usages_daily_pricing_objects)

    def save_usages(self, post_data):
        logger.info("Saving usages for service {}".format(
            post_data['pricing_service']
        ))
        daily_usages, usages_daily_pricing_objects = self.get_usages(post_data)
        self.remove_previous_daily_usages(
            post_data.get('overwrite'),
            post_data['date'],
            usages_daily_pricing_objects,
        )
        DailyUsage.objects.bulk_create(daily_usages)

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import urllib

from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase

from ralph_scrooge.models import DailyUsage, ServiceUsageTypes
from ralph_scrooge.api import (
    PricingServiceUsageObject,
    PricingServiceUsageResource,
    UsagesObject,
    UsageObject,
)
from ralph_scrooge.tests import ScroogeTestCaseMixin
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
)


class TestPricingServiceUsagesApi(ScroogeTestCaseMixin, ResourceTestCase):
    def setUp(self):
        super(TestPricingServiceUsagesApi, self).setUp()
        self.maxDiff = None
        self.resource = 'pricingserviceusages'
        self.user = User.objects.create_user(
            'ralph',
            'ralph@ralph.local',
            'ralph'
        )
        self.date = datetime.date(2013, 10, 10)

        self.today = datetime.date.today()

        self.pricing_service = PricingServiceFactory()

        self.service_environment1 = ServiceEnvironmentFactory()
        self.service_environment2 = ServiceEnvironmentFactory()
        self.service_environment3 = ServiceEnvironmentFactory()
        self.pricing_object1 = PricingObjectFactory()
        self.pricing_object2 = PricingObjectFactory()

        self.usage_type1 = UsageTypeFactory()
        self.usage_type2 = UsageTypeFactory()

        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
            percent=50,
        )
        ServiceUsageTypes.objects.create(
            usage_type=self.usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date.min,
            end=datetime.date.max,
            percent=50,
        )

        self.api_key = self.create_apikey(
            self.user.username,
            self.user.api_key.key,
        )

    def _get_sample(self, overwrite=None):
        pricing_service_usages = PricingServiceUsageObject(
            date=self.date,
            pricing_service=self.pricing_service.name,
            usages=[
                UsagesObject(
                    service=self.service_environment1.service.name,
                    environment=self.service_environment1.environment.name,
                    usages=[
                        UsageObject(symbol=self.usage_type1.symbol, value=123),
                        UsageObject(symbol=self.usage_type2.symbol, value=1.2),
                    ]
                ),
                UsagesObject(
                    service_id=self.service_environment2.service.id,
                    environment=self.service_environment2.environment.name,
                    usages=[
                        UsageObject(symbol=self.usage_type1.symbol, value=321),
                        UsageObject(symbol=self.usage_type2.symbol, value=11),
                    ]
                ),
                UsagesObject(
                    pricing_object=self.pricing_object1.name,
                    usages=[
                        UsageObject(symbol=self.usage_type1.symbol, value=3.3),
                        UsageObject(symbol=self.usage_type2.symbol, value=44),
                    ]
                )
            ]
        )
        if overwrite is not None:
            pricing_service_usages.overwrite = overwrite
        return pricing_service_usages

    def _compare_sample_usages(self):
        self.assertEquals(DailyUsage.objects.count(), 6)

        daily_usage_1 = DailyUsage.objects.order_by('id')[0]
        self.assertEquals(
            daily_usage_1.service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usage_1.date, self.date)
        self.assertEquals(daily_usage_1.type, self.usage_type1)
        self.assertEquals(daily_usage_1.value, 123)

        daily_usage_2 = DailyUsage.objects.order_by('id')[5]
        self.assertEquals(
            daily_usage_2.service_environment,
            self.pricing_object1.service_environment
        )
        self.assertEquals(daily_usage_2.date, self.date)
        self.assertEquals(daily_usage_2.type, self.usage_type2)
        self.assertEquals(daily_usage_2.value, 44)

    def test_save_usages(self):
        pricing_service_usages = self._get_sample()
        PricingServiceUsageResource.save_usages(pricing_service_usages)
        self._compare_sample_usages()

    def test_to_dict(self):
        service_usages = self._get_sample()
        self.assertEquals(service_usages.to_dict(), {
            'pricing_service': self.pricing_service.name,
            'pricing_service_id': None,
            'date': self.date,
            'overwrite': 'no',
            'usages': [
                {
                    'service': self.service_environment1.service.name,
                    'service_id': None,
                    'environment': self.service_environment1.environment.name,
                    'pricing_object': None,
                    'usages': [
                        {
                            'symbol': self.usage_type1.symbol,
                            'value': 123,
                        },
                        {
                            'symbol': self.usage_type2.symbol,
                            'value': 1.2,
                        },
                    ]
                },
                {
                    'service': None,
                    'service_id': self.service_environment2.service.id,
                    'environment': self.service_environment2.environment.name,
                    'pricing_object': None,
                    'usages': [
                        {
                            'symbol': self.usage_type1.symbol,
                            'value': 321,
                        },
                        {
                            'symbol': self.usage_type2.symbol,
                            'value': 11,
                        },
                    ]
                },
                {
                    'service': None,
                    'service_id': None,
                    'environment': None,
                    'pricing_object': self.pricing_object1.name,
                    'usages': [
                        {
                            'symbol': self.usage_type1.symbol,
                            'value': 3.3,
                        },
                        {
                            'symbol': self.usage_type2.symbol,
                            'value': 44,
                        },
                    ]
                },
            ]
        })

    def test_api(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 201)
        self._compare_sample_usages()

    def test_api_pricing_service_id(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        del data['pricing_service']
        data['pricing_service_id'] = self.pricing_service.id
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 201)
        self._compare_sample_usages()

    def test_api_invalid_pricing_service(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        ps_name = 'invalid_service'
        data['pricing_service'] = ps_name
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            'Invalid pricing service name ({}) or id (None)'.format(ps_name)
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def test_api_invalid_service(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        service = 'invalid_service'
        del data['usages'][1]['service_id']
        data['usages'][1]['service'] = service
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            'Invalid service or environment name ({} / {})'.format(
                service,
                data['usages'][1]['environment']
            )
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def test_api_invalid_environment(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        environment = 'invalid_environment'
        data['usages'][1]['environment'] = environment
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            'Invalid service or environment name ({} / {})'.format(
                data['usages'][1]['service'],
                environment
            )
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def test_missing_service(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        del data['usages'][1]['service_id']
        del data['usages'][1]['service']
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            (
                "Pricing Object (Host, IP etc) or Service and "
                "Environment has to be provided"
            )
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def test_missing_environment(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        del data['usages'][1]['environment']
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            (
                "Pricing Object (Host, IP etc) or Service and "
                "Environment has to be provided"
            )
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def test_missing_pricing_object(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        del data['usages'][2]['pricing_object']
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            (
                "Pricing Object (Host, IP etc) or Service and "
                "Environment has to be provided"
            )
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def test_api_invalid_usage(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        usage_type_symbol = 'invalid_usage'
        data['usages'][1]['usages'][1]['symbol'] = usage_type_symbol
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 400)
        self.assertEquals(
            resp.content,
            'Invalid usage type symbol: {}'.format(usage_type_symbol)
        )
        self.assertEquals(DailyUsage.objects.count(), 0)

    def _basic_call(self):
        service_usages = self._get_sample()
        data = service_usages.to_dict()
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 201)
        usages = DailyUsage.objects.filter(type=self.usage_type1).values_list(
            'service_environment',
            'value',
        )
        self.assertEquals(dict(usages), {
            self.service_environment1.id: 123.0,
            self.service_environment2.id: 321,
            self.pricing_object1.service_environment.id: 3.3,
        })

    def test_overwrite_values_only(self):
        self._basic_call()

        service_usages = self._get_sample(
            overwrite='values_only'
        )
        service_usages.usages[2].pricing_object = self.pricing_object2.name
        data = service_usages.to_dict()
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 201)
        usages = DailyUsage.objects.filter(type=self.usage_type1).values_list(
            'service_environment',
            'value',
        )
        self.assertEquals(dict(usages), {
            self.service_environment1.id: 123.0,
            self.service_environment2.id: 321,
            self.pricing_object1.service_environment.id: 3.3,
            self.pricing_object2.service_environment.id: 3.3,
        })

    def test_overwrite_delete_all_previous(self):
        self._basic_call()

        service_usages = self._get_sample(
            overwrite='delete_all_previous'
        )
        service_usages.usages[0].service = self.service_environment3.service.name  # noqa
        service_usages.usages[0].environment = self.service_environment3.environment.name  # noqa
        data = service_usages.to_dict()
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 201)
        usages = DailyUsage.objects.filter(type=self.usage_type1).values_list(
            'service_environment',
            'value',
        )
        self.assertEquals(dict(usages), {
            self.service_environment3.id: 123.0,
            self.service_environment2.id: 321,
            self.pricing_object1.service_environment.id: 3.3,
        })

    def test_not_overwriting(self):
        self._basic_call()

        service_usages = self._get_sample(
            overwrite='no'
        )
        service_usages.usages[2].pricing_object = self.pricing_object2.name
        data = service_usages.to_dict()
        resp = self.api_client.post(
            '/scrooge/api/v0.9/{0}/'.format(self.resource),
            format='json',
            authentication=self.api_key,
            data=data
        )
        self.assertEquals(resp.status_code, 201)
        usages = DailyUsage.objects.filter(type=self.usage_type1).values_list(
            'service_environment',
            'value',
        )
        self.assertEquals(set(usages), set([
            (self.service_environment1.id, 123.0),
            (self.service_environment2.id, 321),
            (self.pricing_object1.service_environment.id, 3.3),
            (self.service_environment1.id, 123.0),
            (self.service_environment2.id, 321),
            (self.pricing_object2.service_environment.id, 3.3),
        ]))

    def test_get_pricing_service_usages(self):
        self._basic_call()
        resp = self.api_client.get(
            urllib.quote('/scrooge/api/v0.9/{0}/{1}/{2}/'.format(
                self.resource,
                self.pricing_service.id,
                self.date.strftime('%Y-%m-%d'),
            )),
            authentication=self.api_key,
        )
        self.assertEquals(resp.status_code, 200)
        # customize usages dict to response
        compare_to = self._get_sample().to_dict(exclude_empty=True)
        compare_to['date'] = compare_to['date'].strftime('%Y-%m-%d')
        del compare_to['overwrite']  # remove overwrite
        # add service and environment when pricing object is returned
        po1_se = self.pricing_object1.service_environment
        compare_to['usages'][2].update({
            'environment': po1_se.environment.name,
            'service': po1_se.service.name,
            'service_id': po1_se.service.id,
        })
        compare_to['usages'][1]['service'] = self.service_environment2.service.name  # noqa
        # add service_id
        compare_to['usages'][0]['service_id'] = self.service_environment1.service.id  # noqa
        self.assertItemsEqual(compare_to, json.loads(resp.content))

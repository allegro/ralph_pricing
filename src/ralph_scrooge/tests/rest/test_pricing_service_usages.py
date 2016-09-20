# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
from copy import deepcopy

from django.core.urlresolvers import reverse
from django.test import TestCase

from ralph_scrooge.models import DailyUsage, ServiceUsageTypes
# from ralph_scrooge.rest.pricing_service_usages import (
#     # XXX
# )
from ralph_scrooge.tests.utils.factory import (
    PricingObjectFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
)
from rest_framework.test import APIClient

# XXX
from ralph_scrooge.models import (
    DailyUsage,
    PricingObject,
    PricingService,
    ServiceEnvironment,
    UsageType,
)

def print_state():
    print('PricingService:')
    print(PricingService.objects.all())
    print('\n')
    print('ServiceEnvironment:')
    print(ServiceEnvironment.objects.all())
    print('\n')
    print('PricingObject:')
    print(PricingObject.objects.all())
    print('\n')
    print('UsageType:')
    print(UsageType.objects.all())
    print('\n')
    print('ServiceUsageTypes:')
    print(ServiceUsageTypes.objects.all())
    print('\n')
    print('DailyUsage:')
    print(DailyUsage.objects.all())
    print('\n')


class TestPricingServiceUsages(TestCase):

    def compare_usages(self):
        # XXX why only the first one..?
        daily_usage1 = DailyUsage.objects.order_by('id')[0]
        self.assertEquals(
            daily_usage1.service_environment,
            self.service_environment
        )
        self.assertEquals(daily_usage1.date, self.date)
        self.assertEquals(daily_usage1.type, self.usage_type1)
        self.assertEquals(daily_usage1.value, 50)  # XXX

    def setUp(self):
        self.date = datetime.date(2016, 9, 8)
        self.today = datetime.date.today()
        client = APIClient()
        self.pricing_service = PricingServiceFactory()
        self.pricing_object = PricingObjectFactory()
        self.service_environment = self.pricing_object.service_environment
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

        self.pricing_service_usage = {
            "pricing_service": self.pricing_service.name,
            "date": "2016-09-08",
            "usages": [
                {
                    "pricing_object": self.pricing_object.name,
                    "usages": [
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 50,
                        },
                        {
                            "symbol": self.usage_type1.symbol,
                            "value": 50,
                        },
                    ]
                }
            ]
        }


    def test_for_success_when_valid_pricing_object_data_given(self):
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(self.pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.compare_usages()


    def test_for_success_when_valid_service_data_given(self):
        del self.pricing_service_usage['usages'][0]['pricing_object']
        self.pricing_service_usage['usages'][0]['service'] = (
            self.pricing_object.service_environment.service.name
        )
        self.pricing_service_usage['usages'][0]['environment'] = (
            self.pricing_object.service_environment.environment.name
        )
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(self.pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.compare_usages()


    def test_for_success_when_valid_service_id_data_given(self):
        del self.pricing_service_usage['usages'][0]['pricing_object']
        self.pricing_service_usage['usages'][0]['service_id'] = (
            self.pricing_object.service_environment.service_id
        )
        self.pricing_service_usage['usages'][0]['environment'] = (
            self.pricing_object.service_environment.environment.name
        )
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(self.pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.compare_usages()


    def test_for_success_when_valid_service_uid_data_given(self):
        del self.pricing_service_usage['usages'][0]['pricing_object']
        self.pricing_service_usage['usages'][0]['service_uid'] = (
            self.pricing_object.service_environment.service.ci_uid
        )
        self.pricing_service_usage['usages'][0]['environment'] = (
            self.pricing_object.service_environment.environment.name
        )
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(self.pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 201)
        self.compare_usages()


    def test_for_error_when_invalid_pricing_service_given(self):
        self.pricing_service_usage['pricing_service'] = 'fake_service'
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(self.pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['pricing_service']
        self.assertEquals(len(errors), 1)
        self.assertIn('fake_service', errors[0])


    def test_for_error_when_invalid_service_given(self):
        del self.pricing_service_usage['usages'][0]['pricing_object']
        self.pricing_service_usage['usages'][0]['service'] = 'fake_service'
        self.pricing_service_usage['usages'][0]['environment'] = (
            self.pricing_object.service_environment.environment.name
        )
        resp = self.client.post(
            reverse('create_pricing_service_usages'),
            json.dumps(self.pricing_service_usage),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, 400)
        errors = json.loads(resp.content)['usages'][0]['non_field_errors']
        self.assertEquals(len(errors), 1)
        self.assertIn('fake_service', errors[0])
        self.assertIn('does not exist', errors[0])


    # def test_for_error_when_invalid_service_id_given(self):
    #     pass

    # def test_for_error_when_invalid_service_uid_given(self):
    #     pass

    # def test_for_error_when_invalid_environment_given(self):
    #     pass

    # def test_for_error_when_invalid_usage_given(self):
    #     pass

    # XXX Consider adding 'missing' variant for the tests above.


    # def test_overwrite_values_only(self):
    #     resp = self.client.post(
    #         reverse('create_pricing_service_usages'),
    #         json.dumps(self.pricing_service_usage),
    #         content_type='application/json',
    #     )
    #     self.assertEquals(resp.status_code, 201)
    #     self.compare_usages()
    #     self.assertEquals(DailyUsage.objects.count(), 2)
    #     self.assertEquals(DailyUsage.objects.all()[0].value, 50)
    #     self.assertEquals(DailyUsage.objects.all()[1].value, 50)

    #     # before:
    #     # ut13, 50
    #     # ut13, 50
    #     #
    #     # after:
    #     # ut14, 60
    #     # ut13, 40

    #     self.pricing_service_usage['overwrite'] = 'values_only'
    #     self.pricing_service_usage['usages'][0]['usages'][0]['symbol'] = self.usage_type2.symbol
    #     self.pricing_service_usage['usages'][0]['usages'][0]['value'] = 60
    #     self.pricing_service_usage['usages'][0]['usages'][1]['value'] = 40
    #     resp = self.client.post(
    #         reverse('create_pricing_service_usages'),
    #         json.dumps(self.pricing_service_usage),
    #         content_type='application/json',
    #     )
    #     print_state(); assert False
    #     self.assertEquals(resp.status_code, 201)
    #     # self.compare_usages()  # XXX
    #     self.assertEquals(DailyUsage.objects.count(), 2)
    #     self.assertEquals(DailyUsage.objects.all()[0].value, new_value)
    #     self.assertEquals(DailyUsage.objects.all()[1].value, new_value)

    #     # same ('previous') DailyUsage == same date and same UsageType

    #     # XXX what is DailyPricingObject..? what's the difference between DailyUsage..?



    # def test_overwrite_delete_all_previous(self):
    #     pass

    # def test_not_overwriting_by_default(self):
    #     pass


    # def test_get_pricing_service_usages(self):
    #     pass

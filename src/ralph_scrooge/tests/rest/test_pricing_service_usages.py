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


PRICING_SERVICE_USAGE_TEMPLATE = {
    "pricing_service": "service-1",
    "date": "2016-09-08",
    "usages": [],
}

USAGE_TEMPLATE_PRICING_OBJECT = {
    "pricing_object": "some.hostname.net",
    "usages": [
        {
            "symbol": "symbol-1",
            "value": 40
        }  # add more of them if needed
    ]
}

USAGE_TEMPLATE_SERVICE = {
    "service": "service1",
    "environment": "env1",
    "usages": [
        {
            "symbol": "requests",
            "value": 123
        }
    ]
}

USAGE_TEMPLATE_SERVICE_ID = {
    "service_id": 1,
    "environment": "env1",
    "usages": [
        {
            "symbol": "requests",
            "value": 123
        }
    ]
}

USAGE_TEMPLATE_SERVICE_UID = {
    "service_uid": "sc-123",
    "environment": "env1",
    "usages": [
        {
            "symbol": "requests",
            "value": 123
        }
    ]
}


class TestPricingServiceUsages(TestCase):

    def compare_usages(self):
        daily_usage1 = DailyUsage.objects.order_by('id')[0]
        self.assertEquals(
            daily_usage1.service_environment,
            self.service_environment1
        )
        self.assertEquals(daily_usage1.date, self.date)
        self.assertEquals(daily_usage1.type, self.usage_type1)
        self.assertEquals(daily_usage1.value, 123)

    def setUp(self):
        self.date = datetime.date(2016, 9, 8)
        self.today = datetime.date.today()
        client = APIClient()
        self.pricing_service = PricingServiceFactory()
        self.service_environment = ServiceEnvironmentFactory()
        self.pricing_object = PricingObjectFactory()
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

    def test_if_usage_saves_correctly(self):

        pricing_service_usage = deepcopy(PRICING_SERVICE_USAGE_TEMPLATE)
        pricing_object = deepcopy(USAGE_TEMPLATE_PRICING_OBJECT)
        pricing_service_usage['usages'].append(pricing_object)
        pricing_service_usage['usages'].append(pricing_object)

        resp = self.client.post(
            reverse('pricing_service_usages'),
            pricing_service_usage,
            format='json',
        )
        self.assertEquals(resp.status_code, 201)
        self.compare_usages()


    # def test_if_usage_saves_correctly_with_existing_pricing_service(self):
    #     pass

    # def test_for_error_when_invalid_pricing_service_given(self):
    #     pass

    # def test_for_error_when_invalid_service_given(self):
    #     pass

    # def test_for_error_when_invalid_environment_given(self):
    #     pass

    # def test_for_error_when_service_is_missing(self):
    #     pass

    # def test_for_error_when_environment_is_missing(self):
    #     pass

    # def test_for_error_when_pricing_object_is_missing(self):
    #     pass

    # def test_for_error_when_invalid_usage_given(self):
    #     pass

    # def test_overwrite_values_only(self):
    #     pass

    # def test_overwrite_delete_all_previous(self):
    #     pass

    # def test_not_overwriting(self):
    #     pass

    # def test_get_pricing_service_usages(self):
    #     pass

    # # # XXX to be removed
    # # def test_post(self):
    # #     client = APIClient()
    # #     resp = client.post(
    # #         reverse('pricing_service_usages'),
    # #         {'aaa': 'bbb'},
    # #         format='json',
    # #     )

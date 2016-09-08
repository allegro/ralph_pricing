# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from ralph_scrooge.rest.components import ComponentsContent
from ralph_scrooge.tests.utils.factory import (
    CostDateStatusFactory,
    DailyAssetInfoFactory,
    DailyCostFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
)
from rest_framework.test import APIClient

USAGE_TEMPLATE_1 = {
    "pricing_service": "service-1",
    "date": "2016-09-08",
    "usages": [
        {
            "pricing_object": "some.hostname.net",
            "usages": [
                {
                    "symbol": "symbol-1",
                    "value": 40
                }
            ]
        }
    ]
}

class TestPricingServiceUsages(TestCase):

    def setUp(self):
        pass

    def test_if_usage_saves_correctly(self):
        pass

    # XXX to be removed
    def test_post(self):
        client = APIClient()
        resp = client.post(
            reverse('pricing_service_usages'),
            {'aaa': 'bbb'},
            format='json',
        )

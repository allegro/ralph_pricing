# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
from decimal import Decimal

from django.contrib.auth.models import User
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


class TestPricingObjects(TestCase):
    def setUp(self):
        self.components = ComponentsContent()
        self.se1 = ServiceEnvironmentFactory()
        self.se2 = ServiceEnvironmentFactory(
            service=self.se1.service,
        )
        self.se3 = ServiceEnvironmentFactory()
        self.today = datetime.date(2014, 10, 11)
        self.tomorrow = datetime.date(2014, 10, 12)
        self.today_accepted = CostDateStatusFactory(
            date=self.today,
            accepted=True
        )

        self.ut1 = UsageTypeFactory()
        self.ut2 = PricingServiceFactory()

        self.dpo1, self.dpo2 = DailyAssetInfoFactory.create_batch(
            2,
            service_environment=self.se1,
            pricing_object__service_environment=self.se1,
            date=self.today,
        )
        self.dpo3 = DailyAssetInfoFactory(
            service_environment=self.se2,
            pricing_object__service_environment=self.se2,
            date=self.today,
        )
        self.dpo3 = DailyAssetInfoFactory(
            service_environment=self.se3,
            pricing_object__service_environment=self.se3,
            date=self.today,
        )
        self.dpo4 = DailyAssetInfoFactory(
            service_environment=self.se1,
            pricing_object__service_environment=self.se1,
            date=self.tomorrow,
        )
        self.dc1 = DailyCostFactory(
            type=self.ut1,
            pricing_object=self.dpo1.pricing_object,
            service_environment=self.se1,
            date=self.today,
            value=10,
            cost=20,
        )
        self.dc2 = DailyCostFactory(
            type=self.ut1,
            pricing_object=self.dpo1.pricing_object,
            service_environment=self.se1,
            date=self.today,
            value=20,
            cost=30,
        )
        self.dc3 = DailyCostFactory(
            type=self.ut2,
            pricing_object=self.dpo1.pricing_object,
            service_environment=self.se1,
            date=self.today,
            value=25,
            cost=35,
        )
        self.maxDiff = None

    def test_pricing_objects_view_returns_data_from_pricing_objects(self):
        User.objects.create_superuser('test', 'test@test.test', 'test')
        client = APIClient()
        client.login(username='test', password='test')
        resp = client.get(
            reverse(
                'pricing_object_costs',
                args=[
                    self.se1.service.id,
                    self.se1.environment.id,
                    self.today.strftime('%Y-%m-%d'),
                    self.today.strftime('%Y-%m-%d')
                ]
            )
        )
        data = json.loads(resp.content)
        self.assertSetEqual(
            {Decimal(x['2']) for x in data[0]['value'][0]['__nested']},
            {Decimal('50.0'), Decimal('35.0')}
        )

    def test_pricing_objects_view_returns_data_for_other_costs(self):
        daily_cost = DailyCostFactory(
            type=self.ut2,
            pricing_object=None,
            service_environment=self.se1,
            forecast=False,
            date=self.today,
            value=99,
            cost=99,
        )
        User.objects.create_superuser('test', 'test@test.test', 'test')
        client = APIClient()
        client.login(username='test', password='test')
        resp = client.get(
            reverse(
                'pricing_object_costs',
                args=[
                    self.se1.service.id,
                    self.se1.environment.id,
                    self.today.strftime('%Y-%m-%d'),
                    self.today.strftime('%Y-%m-%d')
                ]
            )
        )
        data = json.loads(resp.content)
        self.assertEqual(
            data[-1],
            {
                'icon_class': 'fa-desktop',
                'name': 'Other',
                'color': '#ff0000',
                'value': [{
                    '0': daily_cost.type.name,
                    '1': 99.0,
                    '2': '99.000000'
                }],
                'slug': 'dummy',
                'schema': {
                    '1': 'Value',
                    '0': 'Name',
                    '2': 'Cost'
                }
            }
        )

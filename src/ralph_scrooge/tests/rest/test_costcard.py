# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import datetime
from decimal import Decimal as D

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ralph_scrooge.tests.utils import factory


class TestCardCost(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.month = 11
        self.year = 2014
        self.value = D(100)

        self.service = factory.ServiceFactory()
        self.environment = factory.EnvironmentFactory()
        self.service_environment = factory.ServiceEnvironmentFactory(
            service=self.service,
            environment=self.environment,
        )

        self.base_usage = factory.BaseUsageFactory()
        self.daily_cost = factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=1),
            service_environment=self.service_environment,
            cost=self.value,
            type=self.base_usage,
            verified=True,
        )
        self.daily_cost = factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=2),
            service_environment=self.service_environment,
            cost=self.value,
            type=self.base_usage,
            verified=True,
        )
        self.daily_cost = factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=2),
            service_environment=self.service_environment,
            cost=self.value,
            type=self.base_usage,
        )

    def test_get_cost_card(self):
        response = self.client.get(
            '/scrooge/rest/costcard/{0}/{1}/{2}/{3}/'.format(
                self.service.id,
                self.environment.id,
                self.year,
                self.month,
            )
        )
        self.assertEquals(
            json.loads(response.content),
            [{
                'cost': '200.000000', 'name': self.base_usage.name,
            }, {
                'cost': '200.000000', 'name': 'Total'
            }],
        )

    def test_get_when_wrong_service(self):
        response = self.client.get(
            '/scrooge/rest/costcard/{0}/{1}/{2}/{3}/'.format(
                9999999,
                self.environment.id,
                self.year,
                self.month,
            )
        )

        self.assertFalse(status.is_success(response.status_code))

    def test_get_when_wrong_environment(self):
        response = self.client.get(
            '/scrooge/rest/costcard/{0}/{1}/{2}/{3}/'.format(
                self.service.id,
                99999999,
                self.year,
                self.month,
            )
        )

        self.assertFalse(status.is_success(response.status_code))

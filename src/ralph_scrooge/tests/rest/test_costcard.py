# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import datetime
from decimal import Decimal as D

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.test import APIClient

from ralph_scrooge.tests.utils import factory


class TestCardCost(TestCase):
    def setUp(self):
        User.objects.create_superuser('test', 'test@test.test', 'test')
        self.client = APIClient()
        self.client.login(username='test', password='test')

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

    def _init(self, forecast=False):
        self.daily_cost_1 = factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=1),
            service_environment=self.service_environment,
            cost=self.value,
            type=self.base_usage,
            forecast=forecast,
        )
        self.daily_cost_2 = factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=2),
            service_environment=self.service_environment,
            cost=self.value,
            type=self.base_usage,
            forecast=forecast,
        )
        self.daily_cost_3 = factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=3),
            service_environment=self.service_environment,
            cost=self.value,
            type=self.base_usage,
            forecast=forecast,
        )
        for day in range(1, 3):  # skip 3 day!
            factory.CostDateStatusFactory(
                date=datetime.date(year=self.year, month=self.month, day=day),
                **{'forecast_accepted' if forecast else 'accepted': True}
            )

    def test_get_cost_card(self):
        self._init()
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
            {
                'status': True,
                'results': [{
                    'cost': 200.0, 'name': self.base_usage.name,
                    }, {
                    'cost': 200.0, 'name': 'Total'
                }],
            }
        )

    def test_get_cost_card_forecast(self):
        self._init(forecast=True)
        response = self.client.get(
            '/scrooge/rest/costcard/{0}/{1}/{2}/{3}/?forecast=true'.format(
                self.service.id,
                self.environment.id,
                self.year,
                self.month,
            )
        )
        self.assertEquals(
            json.loads(response.content),
            {
                'status': True,
                'results': [{
                    'cost': 200.0, 'name': self.base_usage.name,
                    }, {
                    'cost': 200.0, 'name': 'Total'
                }],
            }
        )

    def test_get_when_wrong_service(self):
        self._init()
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
        self._init()
        response = self.client.get(
            '/scrooge/rest/costcard/{0}/{1}/{2}/{3}/'.format(
                self.service.id,
                99999999,
                self.year,
                self.month,
            )
        )

        self.assertFalse(status.is_success(response.status_code))

    def test_get_when_there_are_no_accepted_costs(self):
        factory.DailyCostFactory(
            date=datetime.date(year=self.year, month=self.month, day=1),
            service_environment=self.service_environment,
            cost=0.0,
            type=self.base_usage,
            forecast=True,
        )
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
            {
                'status': False,
                'message': _(
                    'There are no accepted costs for chosen date.'
                    ' Please choose different date or back later.',
                )
            }
        )

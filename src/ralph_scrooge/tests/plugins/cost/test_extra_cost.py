# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal as D

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.extra_cost import ExtraCostPlugin
from ralph_scrooge.tests.utils.factory import (
    ExtraCostTypeFactory,
    ServiceEnvironmentFactory,
)


class TestExtraCostPlugin(TestCase):
    def setUp(self):
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)

        self.extra_cost_type = ExtraCostTypeFactory()
        self.service_environments = ServiceEnvironmentFactory.create_batch(5)
        for se in self.service_environments[:5]:
            models.ExtraCost(
                extra_cost_type=self.extra_cost_type,
                start=self.start,
                end=self.end,
                service_environment=se,
                cost=3000,  # daily cost: 100
                forecast_cost=6000,  # daily cost: 200
            ).save()

    def test_costs(self):
        costs = ExtraCostPlugin.costs(
            date=self.today,
            service_environments=self.service_environments[:3],
            extra_cost_type=self.extra_cost_type,
            forecast=False,
        )
        self.assertEquals(costs, {
            self.service_environments[0].id: [
                {
                    'cost': D('100'),
                    'type': self.extra_cost_type
                }
            ],
            self.service_environments[1].id: [
                {
                    'cost': D('100'),
                    'type': self.extra_cost_type
                }
            ],
            self.service_environments[2].id: [
                {
                    'cost': D('100'),
                    'type': self.extra_cost_type
                }
            ]
        })

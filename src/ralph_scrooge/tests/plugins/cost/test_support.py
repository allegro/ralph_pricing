# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal as D

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.support import SupportPlugin
from ralph_scrooge.tests.utils.factory import PricingObjectFactory


class TestSupportPlugin(TestCase):
    def setUp(self):
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)

        self.support_type = models.ExtraCostType.objects.get(pk=2)
        self.pricing_objects = PricingObjectFactory.create_batch(5)
        self.service_environments = [
            po.service_environment for po in self.pricing_objects
        ]
        # create daily pricing objects
        for po in self.pricing_objects:
            po.get_daily_pricing_object(self.today)
        # create support costs
        for po in self.pricing_objects[:3]:
            models.SupportCost(
                start=self.start,
                end=self.end,
                pricing_object=po,
                cost=3000,  # daily cost: 100
                forecast_cost=6000,  # daily cost: 200
                support_id=1,
            ).save()

    def test_costs(self):
        costs = SupportPlugin.costs(
            date=self.today,
            service_environments=self.service_environments[:5],
            forecast=False,
        )
        self.assertEquals(costs, {
            self.service_environments[0].id: [
                {
                    'type': self.support_type,
                    'cost': D('100'),
                    'pricing_object_id': self.pricing_objects[0].id,
                }
            ],
            self.service_environments[1].id: [
                {
                    'type': self.support_type,
                    'cost': D('100'),
                    'pricing_object_id': self.pricing_objects[1].id,
                }
            ],
            self.service_environments[2].id: [
                {
                    'type': self.support_type,
                    'cost': D('100'),
                    'pricing_object_id': self.pricing_objects[2].id,
                }
            ]
        })

    def test_costs_forecast(self):
        costs = SupportPlugin.costs(
            date=self.today,
            service_environments=self.service_environments[:2],
            forecast=True,
        )
        self.assertEquals(costs, {
            self.service_environments[0].id: [
                {
                    'cost': D('200'),
                    'type': self.support_type,
                    'pricing_object_id': self.pricing_objects[0].id,
                }
            ],
            self.service_environments[1].id: [
                {
                    'cost': D('200'),
                    'type': self.support_type,
                    'pricing_object_id': self.pricing_objects[1].id,
                }
            ],
        })

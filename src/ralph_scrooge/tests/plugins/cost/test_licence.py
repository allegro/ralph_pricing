# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from decimal import Decimal

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.licence import LicencePlugin
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import PricingObjectFactory


class TestLicencePlugin(ScroogeTestCase):

    def setUp(self):
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)

        self.support_type = models.ExtraCostType.objects_admin.get(
            pk=models.EXTRA_COST_TYPES.LICENCE.id
        )
        self.pricing_objects = PricingObjectFactory.create_batch(5)
        self.service_environments = [
            po.service_environment for po in self.pricing_objects
        ]
        # create daily pricing objects
        for po in self.pricing_objects:
            po.get_daily_pricing_object(self.today)
        # create licence costs
        for po in self.pricing_objects[:3]:
            models.LicenceCost(
                start=self.start,
                end=self.end,
                pricing_object=po,
                cost=3000,  # daily cost: 100
                forecast_cost=6000,  # daily cost: 200
                licence_id=1,
            ).save()

    def test_costs(self):
        costs = LicencePlugin.costs(
            date=self.today,
            service_environments=self.service_environments[:5],
            forecast=False,
        )

        self.assertEquals(costs, {
            self.service_environments[0].id: [
                {
                    'type': self.support_type,
                    'cost': Decimal('100'),
                    'pricing_object_id': self.pricing_objects[0].id,
                }
            ],
            self.service_environments[1].id: [
                {
                    'type': self.support_type,
                    'cost': Decimal('100'),
                    'pricing_object_id': self.pricing_objects[1].id,
                }
            ],
            self.service_environments[2].id: [
                {
                    'type': self.support_type,
                    'cost': Decimal('100'),
                    'pricing_object_id': self.pricing_objects[2].id,
                }
            ]
        })

    def test_costs_forecast(self):
        costs = LicencePlugin.costs(
            date=self.today,
            service_environments=self.service_environments[:2],
            forecast=True,
        )

        self.assertEquals(costs, {
            self.service_environments[0].id: [
                {
                    'cost': Decimal('200'),
                    'type': self.support_type,
                    'pricing_object_id': self.pricing_objects[0].id,
                }
            ],
            self.service_environments[1].id: [
                {
                    'cost': Decimal('200'),
                    'type': self.support_type,
                    'pricing_object_id': self.pricing_objects[1].id,
                }
            ],
        })

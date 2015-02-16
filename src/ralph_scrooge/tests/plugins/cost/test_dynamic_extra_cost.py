# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.dynamic_extra_cost import (
    NoPriceCostError,
    DynamicExtraCostPlugin,
)
from ralph_scrooge.tests.utils.factory import (
    DynamicExtraCostFactory,
    DynamicExtraCostTypeFactory,
    DynamicExtraCostDivisionFactory,
    ServiceEnvironmentFactory,
)


class TestDynamicExtraCostPlugin(TestCase):
    def setUp(self):
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)
        self.date_out_of_range = date(2013, 11, 12)

        self.dynamic_extra_cost_type = DynamicExtraCostTypeFactory()
        # division
        self.division = DynamicExtraCostDivisionFactory.create_batch(
            2,
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
        )
        self.usage_types = [d.usage_type for d in self.division]

        # cost
        DynamicExtraCostFactory(
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
            start=self.start,
            end=self.end,
            cost=300,
            forecast_cost=600,
        )

    def _create_usages(self):
        self.service_environments = ServiceEnvironmentFactory.create_batch(2)
        for usage_type in self.usage_types:
            for se, value in zip(self.service_environments, [30, 70]):
                dpo = se.dummy_pricing_object
                for day in rrule.rrule(
                    rrule.DAILY,
                    dtstart=self.start,
                    until=self.end
                ):
                    models.DailyUsage.objects.create(
                        date=day,
                        service_environment=se,
                        daily_pricing_object=dpo.get_daily_pricing_object(day),
                        type=usage_type,
                        value=value,
                    )

    def test_get_costs(self):
        result = DynamicExtraCostPlugin._get_costs(
            date=self.today,
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
            forecast=False,
        )
        self.assertEquals(result, {
            self.dynamic_extra_cost_type.id: (10, None)
        })

    def test_get_costs_forecast(self):
        result = DynamicExtraCostPlugin._get_costs(
            date=self.today,
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
            forecast=True,
        )
        self.assertEquals(result, {
            self.dynamic_extra_cost_type.id: (20, None)
        })

    def test_get_costs_not_found(self):
        with self.assertRaises(NoPriceCostError):
            DynamicExtraCostPlugin._get_costs(
                date=self.date_out_of_range,
                dynamic_extra_cost_type=self.dynamic_extra_cost_type,
                forecast=False,
            )

    def test_get_percentage(self):
        result = DynamicExtraCostPlugin._get_percentage(
            date=self.today,
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
        )
        self.assertEquals(set(result), set(self.division))

    def test_total_cost_not_collapsed(self):
        self._create_usages()
        result = DynamicExtraCostPlugin.total_cost(
            date=self.today,
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
            service_environments=self.service_environments,
        )
        self.assertEquals(result, {
            self.dynamic_extra_cost_type.id: [D(10), {}]
        })

    def test_costs(self):
        self._create_usages()
        result = DynamicExtraCostPlugin(
            type='costs',
            date=self.today,
            dynamic_extra_cost_type=self.dynamic_extra_cost_type,
            service_environments=self.service_environments,
        )
        se1, se2 = self.service_environments
        self.assertEquals(result, {
            se1.id: [
                {
                    'cost': D(3),
                    'pricing_object_id': se1.dummy_pricing_object.id,
                    'type_id': self.dynamic_extra_cost_type.id,
                }
            ],
            se2.id: [
                {
                    'cost': D(7),
                    'pricing_object_id': se2.dummy_pricing_object.id,
                    'type_id': self.dynamic_extra_cost_type.id,
                }
            ]
        })

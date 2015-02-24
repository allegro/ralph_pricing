# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from decimal import Decimal as D
import mock

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.pricing_service_fixed_price import (
    PricingServiceFixedPricePlugin,
)
from ralph_scrooge.tests.utils.factory import (
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
)


class TestPricingServiceFixedPricePluginPlugin(TestCase):
    def setUp(self):
        self.today = date(2013, 10, 10)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)
        self.pricing_service = PricingServiceFactory()
        self.service_usage_types = UsageTypeFactory.create_batch(
            2,
            usage_type='SU',
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[0],
            pricing_service=self.pricing_service,
            start=self.start,
            end=self.end,
        )
        models.ServiceUsageTypes.objects.create(
            usage_type=self.service_usage_types[1],
            pricing_service=self.pricing_service,
            start=self.start,
            end=self.end,
        )
        self.service_environments = ServiceEnvironmentFactory.create_batch(2)
        self.maxDiff = None

    @mock.patch('ralph_scrooge.plugins.cost.pricing_service_fixed_price.plugin_runner.run')  # noqa
    def test_costs(self, plugin_runner_mock):
        def effect(
            chain,
            plugin_name,
            type,
            date,
            usage_type,
            forecast,
            *args,
            **kwargs
        ):
            if usage_type == self.service_usage_types[0]:
                return {
                    self.service_environments[0].id: [
                        {
                            'pricing_object_id': 1,
                            'type_id': self.service_usage_types[0].id,
                            'cost': D(100),
                            'value': 100,
                        },
                        {
                            'pricing_object_id': 2,
                            'type_id': self.service_usage_types[0].id,
                            'cost': D(200),
                            'value': 200,
                        },
                    ],
                    self.service_environments[1].id: [
                        {
                            'pricing_object_id': 3,
                            'type_id': self.service_usage_types[0].id,
                            'cost': D(300),
                            'value': 300,
                        }
                    ]
                }
            return {
                self.service_environments[0].id: [
                    {
                        'pricing_object_id': 1,
                        'type_id': self.service_usage_types[1].id,
                        'cost': D(300),
                        'value': 300,
                    },
                ],
                self.service_environments[1].id: [
                    {
                        'pricing_object_id': 3,
                        'type_id': self.service_usage_types[1].id,
                        'cost': D(400),
                        'value': 400,
                    }
                ]
            }
        plugin_runner_mock.side_effect = effect
        costs = PricingServiceFixedPricePlugin(
            type='costs',
            pricing_service=self.pricing_service,
            date=self.today,
            service_environments=self.service_environments,
        )
        self.assertEquals(costs, {
            self.service_environments[0].id: [
                {
                    'type_id': self.pricing_service.id,
                    'pricing_object_id': 1,
                    'cost': D(400),
                    '_children': [
                        {
                            'pricing_object_id': 1,
                            'type_id': self.service_usage_types[0].id,
                            'cost': D(100),
                            'value': 100,
                        },
                        {
                            'pricing_object_id': 1,
                            'type_id': self.service_usage_types[1].id,
                            'cost': D(300),
                            'value': 300,
                        },
                    ]
                },
                {
                    'type_id': self.pricing_service.id,
                    'pricing_object_id': 2,
                    'cost': D(200),
                    '_children': [
                        {
                            'pricing_object_id': 2,
                            'type_id': self.service_usage_types[0].id,
                            'cost': D(200),
                            'value': 200,
                        },
                    ]
                }
            ],
            self.service_environments[1].id: [
                {
                    'type_id': self.pricing_service.id,
                    'pricing_object_id': 3,
                    'cost': D(700),
                    '_children': [
                        {
                            'pricing_object_id': 3,
                            'type_id': self.service_usage_types[0].id,
                            'cost': D(300),
                            'value': 300,
                        },
                        {
                            'pricing_object_id': 3,
                            'type_id': self.service_usage_types[1].id,
                            'cost': D(400),
                            'value': 400,
                        },
                    ]
                },
            ],
        })

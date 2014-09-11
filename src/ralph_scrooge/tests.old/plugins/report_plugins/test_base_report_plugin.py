# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from dateutil import rrule

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.reports.base import BaseReportPlugin
from ralph_scrooge.tests import utils
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    ServiceFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


class SampleReportPlugin(BaseReportPlugin):
    def costs(self, *args, **kwargs):
        pass

    def schema(self, *args, **kwargs):
        pass

    def total_cost(self, *args, **kwargs):
        pass


class TestBaseReportPlugin(TestCase):
    def setUp(self):
        self.plugin = SampleReportPlugin()

        # usage types
        self.usage_type = UsageTypeFactory(
            symbol='ut1',
            by_warehouse=False,
            by_cost=False,
            type='BU',
        )
        self.usage_type_cost_wh = UsageTypeFactory(
            symbol='ut2',
            by_warehouse=True,
            by_cost=True,
            type='BU',
        )

        # warehouses
        self.warehouse1 = WarehouseFactory(show_in_report=True)
        self.warehouse2 = WarehouseFactory(show_in_report=True)
        self.warehouses = models.Warehouse.objects.all()

        # services
        self.service1 = ServiceFactory()
        self.service2 = ServiceFactory()
        self.service3 = ServiceFactory()
        self.service4 = ServiceFactory()
        self.services = models.Service.objects.all()

        # daily usages of base type
        # ut1:
        #   service1: 10
        #   service2: 20
        # ut2:
        #   service1: 20 (half in warehouse1, half in warehouse2)
        #   service2: 40 (half in warehouse1, half in warehouse2)
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        base_usage_types = models.UsageType.objects.filter(type='BU')
        for i, ut in enumerate(base_usage_types, start=1):
            days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
            for j, day in enumerate(days, start=1):
                for k, service in enumerate(self.services, start=1):
                    daily_usage = DailyUsageFactory(
                        date=day,
                        service=service,
                        value=10 * i * k,
                        type=ut,
                    )
                    if ut.by_warehouse:
                        daily_usage.warehouse = (
                            self.warehouses[j % len(self.warehouses)]
                        )
                    daily_usage.save()

        # usage prices
        dates = [
            (datetime.date(2013, 10, 5), datetime.date(2013, 10, 12)),
            (datetime.date(2013, 10, 13), datetime.date(2013, 10, 17)),
            (datetime.date(2013, 10, 18), datetime.date(2013, 10, 25)),
        ]
        # (real cost/price, forecast cost/price)
        ut_prices_costs = [
            (self.usage_type, [(10, 50), (20, 60), (30, 70)]),
            (self.usage_type_cost_wh, [
                [(3600, 2400), (5400, 5400), (4800, 12000)],  # warehouse1
                [(3600, 5400), (3600, 1200), (7200, 3600)],  # warehouse2
            ]),
        ]

        def add_usage_price(usage_type, prices_costs, warehouse=None):
            for daterange, price_cost in zip(dates, prices_costs):
                start, end = daterange
                usage_price = models.UsagePrice(
                    type=usage_type,
                    start=start,
                    end=end,
                )
                if warehouse is not None:
                    usage_price.warehouse = warehouse
                if usage_type.by_cost:
                    usage_price.cost = price_cost[0]
                    usage_price.forecast_cost = price_cost[1]
                else:
                    usage_price.price = price_cost[0]
                    usage_price.forecast_price = price_cost[1]
                usage_price.save()

        for ut, prices in ut_prices_costs:
            if ut.by_warehouse:
                for i, prices_wh in enumerate(prices):
                    warehouse = self.warehouses[i]
                    add_usage_price(ut, prices_wh, warehouse)
            else:
                add_usage_price(ut, prices)

    # =========================================================================
    # _get_usages_in_period_per_device
    # =========================================================================
    # TODO: adjust to pricing object (when base plugin report adjusted)
    def _devices_sample(self):
        self.device1 = utils.get_or_create_device()
        self.device2 = utils.get_or_create_device()
        self.service_device = utils.get_or_create_service()
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 20)
        base_usage_types = models.UsageType.objects.filter(type='BU')

        for i, device in enumerate([self.device1, self.device2], start=1):
            for j, ut in enumerate(base_usage_types, start=1):
                for k, day in enumerate(rrule.rrule(
                    rrule.DAILY,
                    dtstart=start,
                    until=end
                )):
                    daily_usage = models.DailyUsage(
                        date=day,
                        service=self.service_device,
                        pricing_device=device,
                        value=10 * i,
                        type=ut,
                    )
                    if ut.by_warehouse:
                        daily_usage.warehouse = (
                            self.warehouses[k % len(self.warehouses)]
                        )
                    daily_usage.save()

    def test_get_usages_in_period_per_device(self):
        self._devices_sample()
        result = self.plugin._get_usages_in_period_per_device(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 25),
            usage_type=self.usage_type,
            services=[self.service_device],
        )
        self.assertEquals(result, [
            {
                'pricing_device': self.device1.id,
                'usage': 110.0,  # 11 (days) * 10 (daily usage)
            },
            {
                'pricing_device': self.device2.id,
                'usage': 220.0,  # 11 (days) * 20 (daily usage)
            }
        ])

    def test_get_usages_in_period_per_device_with_warehouse(self):
        self._devices_sample()
        result = self.plugin._get_usages_in_period_per_device(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 25),
            usage_type=self.usage_type_cost_wh,
            services=[self.service_device],
            warehouse=self.warehouse1,
        )
        self.assertEquals(result, [
            {
                'pricing_device': self.device1.id,
                'usage': 60.0,  # 6 (days with usage) * 10 (daily usage)
            },
            {
                'pricing_device': self.device2.id,
                'usage': 120.0,  # 6 (days with usage) * 20 (daily usage)
            }
        ])

    def test_get_usages_in_period_per_device_excluded_services(self):
        self._devices_sample()
        result = self.plugin._get_usages_in_period_per_device(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 25),
            usage_type=self.usage_type,
            excluded_services=[
                self.service1,
                self.service2,
                self.service3,
                self.service4
            ],
        )
        self.assertEquals(result, [
            {
                'pricing_device': self.device1.id,
                'usage': 110.0,  # 11 (days) * 10 (daily usage)
            },
            {
                'pricing_device': self.device2.id,
                'usage': 220.0,  # 11 (days) * 20 (daily usage)
            }
        ])

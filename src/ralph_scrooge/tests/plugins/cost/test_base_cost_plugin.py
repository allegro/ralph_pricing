# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
from dateutil import rrule
from decimal import Decimal as D

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.base import BaseCostPlugin
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


class SampleCostPlugin(BaseCostPlugin):
    def _costs(self, *args, **kwargs):
        pass


class TestBaseCostPlugin(ScroogeTestCase):
    def setUp(self):
        self.plugin = SampleCostPlugin()

        # usage types
        self.usage_type = UsageTypeFactory(
            symbol='ut1',
            by_warehouse=False,
            by_cost=False,
            usage_type='BU',
        )
        self.usage_type_cost_wh = UsageTypeFactory(
            symbol='ut2',
            by_warehouse=True,
            by_cost=True,
            usage_type='BU',
        )

        # warehouses
        self.default_warehouse = models.Warehouse.objects.get(name='Default')
        self.warehouse1 = WarehouseFactory(show_in_report=True)
        self.warehouse2 = WarehouseFactory(show_in_report=True)
        self.warehouses = models.Warehouse.objects.exclude(
            pk=self.default_warehouse.pk
        )
        # services
        self.service_environment1 = ServiceEnvironmentFactory()
        self.service_environment2 = ServiceEnvironmentFactory()
        self.service_environment3 = ServiceEnvironmentFactory()
        self.service_environment4 = ServiceEnvironmentFactory()
        self.service_environments = models.ServiceEnvironment.objects.all()

        # daily usages of base type
        # ut1:
        #   service1: 10
        #   service2: 20
        # ut2:
        #   service1: 20 (half in warehouse1, half in warehouse2)
        #   service2: 40 (half in warehouse1, half in warehouse2)
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        base_usage_types = models.UsageType.objects.filter(usage_type='BU')
        for i, ut in enumerate(base_usage_types, start=1):
            days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
            for j, day in enumerate(days, start=1):
                for k, service_environment in enumerate(
                    self.service_environments, start=1
                ):
                    daily_usage = DailyUsageFactory(
                        date=day,
                        service_environment=service_environment,
                        value=10 * i * k,
                        type=ut,
                        warehouse=self.default_warehouse,
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
    # _get_price_from_cost
    # =========================================================================
    @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_total_usage')  # noqa
    def test_get_price_from_cost(self, get_total_usage_mock):
        get_total_usage_mock.return_value = 100.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            cost=2000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(usage_price, False)

        self.assertEquals(result, D(20))  # 2000 / 100 = 20
        get_total_usage_mock.assert_called_with(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            usage_type=self.usage_type_cost_wh,
            excluded_services=None,
            excluded_services_environments=None,
            warehouse=None,
            service_environments=None,
        )

    @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_total_usage')  # noqa
    def test_get_price_from_cost_with_warehouse(
        self,
        get_total_usage_mock
    ):
        get_total_usage_mock.return_value = 100.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            cost=2000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(
            usage_price,
            False,
            warehouse=self.warehouse1
        )

        self.assertEquals(result, D(20))  # 2000 / 100 = 20
        get_total_usage_mock.assert_called_with(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            usage_type=self.usage_type_cost_wh,
            excluded_services=None,
            excluded_services_environments=None,
            warehouse=self.warehouse1,
            service_environments=None,
        )

    @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_total_usage')  # noqa
    def test_get_price_from_cost_with_forecast(
        self,
        get_total_usage_mock
    ):
        get_total_usage_mock.return_value = 100.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            forecast_cost=3000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(usage_price, True)

        self.assertEquals(result, D(30))  # 3000 / 100 = 30
        get_total_usage_mock.assert_called_with(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            usage_type=self.usage_type_cost_wh,
            excluded_services=None,
            excluded_services_environments=None,
            warehouse=None,
            service_environments=None,
        )

    @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_total_usage')  # noqa
    def test_get_price_from_cost_total_usage_0(
        self,
        get_total_usage_mock
    ):
        get_total_usage_mock.return_value = 0.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            cost=3000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(usage_price, False)

        self.assertEquals(result, D(0))

    @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_total_usage')  # noqa
    def test_get_price_from_cost_total_excluded_services(
        self,
        get_total_usage_mock
    ):
        get_total_usage_mock.return_value = 10.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            cost=3000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(
            usage_price,
            False,
            excluded_services=[self.service_environment1],
        )

        self.assertEquals(result, D(300))
        get_total_usage_mock.assert_called_with(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            usage_type=self.usage_type_cost_wh,
            excluded_services=[self.service_environment1],
            excluded_services_environments=None,
            warehouse=None,
            service_environments=None,
        )

    # =========================================================================
    # _get_total_usage
    # =========================================================================
    def test_get_total_usage(self):
        result = self.plugin._get_total_usage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
        )
        # 11*(10 + 20 + 30 + 40) = 1100
        self.assertEquals(result, 1100.0)

    def test_get_total_usage_with_warehouse(self):
        result = self.plugin._get_total_usage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse2,
        )
        #  6 * (20 + 40 + 60 + 80)
        # /^\
        #  |
        #  +--- every even day between 10 and 20 (inclusive)
        self.assertEquals(result, 1200.0)

    def test_get_total_usage_with_services(self):
        result = self.plugin._get_total_usage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            service_environments=[self.service_environment1]
        )
        # 11 * 10 = 110
        self.assertEquals(result, 110.0)

    def test_get_total_usage_with_services_and_warehouse(self):
        result = self.plugin._get_total_usage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
            service_environments=[self.service_environment2],
        )
        #  5 * 40 = 200
        # /^\
        #  |
        #  +--- every odd day between 10 and 20 (inclusive)
        self.assertEquals(result, 200.0)

    def test_get_total_usage_with_excluded_services(self):
        result = self.plugin._get_total_usage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
            excluded_services=[self.service_environment2.service],
        )
        #  5 * (20 + 60 + 80)= 800
        # /^\
        #  |
        #  +--- every odd day between 10 and 20 (inclusive)
        self.assertEquals(result, 800.0)

    # =========================================================================
    # _get_usages_per_service_environment
    # =========================================================================
    def test_get_usages_per_service_environment(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
        )
        self.assertEquals(result, [
            {
                'usage': 110.0,  # 11 * 10 = 110
                'service_environment': self.service_environment1.id,
            },
            {
                'usage': 220.0,  # 11 * 20 = 220
                'service_environment': self.service_environment2.id,
            },
            {
                'usage': 330.0,  # 11 * 30 = 330
                'service_environment': self.service_environment3.id,
            },
            {
                'usage': 440.0,  # 11 * 40 = 440
                'service_environment': self.service_environment4.id,
            },
        ])

    def test_get_usages_per_service_environment_with_warehouse(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
        )
        self.assertEquals(result, [
            {
                'usage': 100.0,  # 5 * 20 = 100
                'service_environment': self.service_environment1.id,
            },
            {
                'usage': 200.0,  # 5 * 40 = 200
                'service_environment': self.service_environment2.id,
            },
            {
                'usage': 300.0,  # 5 * 60 = 300
                'service_environment': self.service_environment3.id,
            },
            {
                'usage': 400.0,  # 5 * 80 = 400
                'service_environment': self.service_environment4.id,
            },
        ])

    def test_get_usages_per_service_environment_with_services(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            service_environments=[self.service_environment1],
        )
        self.assertEquals(result, [
            {
                'usage': 110.0,  # 11 * 10 = 110
                'service_environment': self.service_environment1.id,
            },
        ])

    def test_get_usages_per_service_environment_without_services(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            service_environments=[],
        )
        self.assertEquals(result, [])

    def test_get_usages_per_service_environment_with_warehouse_service(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse2,
            service_environments=[self.service_environment2],
        )
        self.assertEquals(result, [
            {
                'usage': 240.0,  # 6 * 40 = 240
                'service_environment': self.service_environment2.id,
            }
        ])

    def test_get_usages_per_service_environment_with_excluded_services(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
            excluded_services=[self.service_environment3.service],
        )
        self.assertEquals(result, [
            {
                'usage': 100.0,  # 5 * 20 = 100
                'service_environment': self.service_environment1.id,
            },
            {
                'usage': 200.0,  # 5 * 40 = 200
                'service_environment': self.service_environment2.id,
            },
            {
                'usage': 400.0,  # 5 * 80 = 400
                'service_environment': self.service_environment4.id,
            },
        ])

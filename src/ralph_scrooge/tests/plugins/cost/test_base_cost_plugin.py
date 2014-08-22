# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase

from ralph_scrooge import models
from ralph_scrooge.plugins.cost.base import BaseCostPlugin
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


class SampleCostPlugin(BaseCostPlugin):
    def costs(self, *args, **kwargs):
        pass


class TestBaseCostPlugin(TestCase):
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
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            None,
            None,
            None,
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
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            self.warehouse1,
            None,
            None,
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
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            None,
            None,
            None
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
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            None,
            None,
            [self.service_environment1]
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
            excluded_services=[self.service_environment2],
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
            {'usage': 110.0, 'service_environment': 1},  # 11 * 10 = 110
            {'usage': 220.0, 'service_environment': 2},  # 11 * 20 = 220
            {'usage': 330.0, 'service_environment': 3},  # 11 * 30 = 330
            {'usage': 440.0, 'service_environment': 4},  # 11 * 40 = 440
        ])

    def test_get_usages_per_service_environment_with_warehouse(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
        )
        self.assertEquals(result, [
            {'usage': 100.0, 'service_environment': 1},  # 5 * 20 = 100
            {'usage': 200.0, 'service_environment': 2},  # 5 * 40 = 200
            {'usage': 300.0, 'service_environment': 3},  # 5 * 60 = 300
            {'usage': 400.0, 'service_environment': 4},  # 5 * 80 = 400
        ])

    def test_get_usages_per_service_environment_with_services(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            service_environments=[self.service_environment1],
        )
        self.assertEquals(result, [
            {'usage': 110.0, 'service_environment': 1},  # 11 * 10 = 110
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
            {'usage': 240.0, 'service_environment': 2}  # 6 * 40 = 240
        ])

    def test_get_usages_per_service_environment_with_excluded_services(self):
        result = self.plugin._get_usages_per_service_environment(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
            excluded_services=[self.service_environment3],
        )
        self.assertEquals(result, [
            {'usage': 100.0, 'service_environment': 1},  # 5 * 20 = 100
            {'usage': 200.0, 'service_environment': 2},  # 5 * 40 = 200
            {'usage': 400.0, 'service_environment': 4},  # 5 * 80 = 400
        ])

    # # =========================================================================
    # # _distribute_costs
    # # =========================================================================
    # @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_usages_per_service_environment')  # noqa
    # @mock.patch('ralph_scrooge.plugins.cost.base.BaseCostPlugin._get_total_usage')  # noqa
    # def test_distribute_costs(self, total_usage_mock, usages_per_service_mock):
    #     percentage = {
    #         self.usage_type.id: 20,
    #         self.usage_type_cost_wh.id: 80,
    #     }

    #     def sample_usages(
    #         start,
    #         end,
    #         usage_type,
    #         warehouse=None,
    #         service_environments=None
    #     ):
    #         usages = {
    #             self.usage_type.id: [
    #                 {
    #                     'service_environment': self.service_environment1.id,
    #                     'usage': 0,
    #                 },
    #                 {
    #                     'service_environment': self.service_environment2.id,
    #                     'usage': 0,
    #                 },
    #                 {
    #                     'service_environment': self.service_environment3.id,
    #                     'usage': 900,
    #                 },
    #                 {
    #                     'service_environment': self.service_environment4.id,
    #                     'usage': 100,
    #                 },
    #             ],
    #             self.usage_type_cost_wh.id: [
    #                 {
    #                     'service_environment': self.service_environment3.id,
    #                     'usage': 1200,
    #                 },
    #                 {
    #                     'service_environment': self.service_environment4.id,
    #                     'usage': 400,
    #                 },
    #             ]
    #         }
    #         return usages[usage_type.id]

    #     def sample_total_usage(start, end, usage_type):
    #         total_usages = {
    #             self.usage_type.id: 1000,
    #             self.usage_type_cost_wh.id: 1600,
    #         }
    #         return total_usages[usage_type.id]

    #     usages_per_service_mock.side_effect = sample_usages
    #     total_usage_mock.side_effect = sample_total_usage

    #     result = self.plugin._distribute_costs(
    #         start=datetime.date(2013, 10, 10),
    #         end=datetime.date(2013, 10, 20),
    #         service_environments=self.service_environments,
    #         cost=10000,
    #         percentage=percentage,
    #     )
    #     usage_type_count = 'ut_{0}_count'.format(self.usage_type.id)
    #     usage_type_cost = 'ut_{0}_cost'.format(self.usage_type.id)
    #     usage_type_cost_wh_count = 'ut_{0}_count'.format(
    #         self.usage_type_cost_wh.id
    #     )
    #     usage_type_cost_wh_cost = 'ut_{0}_cost'.format(
    #         self.usage_type_cost_wh.id
    #     )
    #     self.assertEquals(result, {
    #         self.service_environment1.id: {
    #             usage_type_count: 0,
    #             usage_type_cost: D(0),
    #         },
    #         self.service_environment2.id: {
    #             usage_type_count: 0,
    #             usage_type_cost: D(0),
    #         },
    #         self.service_environment3.id: {
    #             usage_type_count: 900,
    #             usage_type_cost: D('1800'),
    #             usage_type_cost_wh_count: 1200,
    #             usage_type_cost_wh_cost: D('6000'),
    #         },
    #         self.service_environment4.id: {
    #             usage_type_count: 100,
    #             usage_type_cost: D('200'),
    #             usage_type_cost_wh_count: 400,
    #             usage_type_cost_wh_cost: D('2000'),
    #         },
    #     })

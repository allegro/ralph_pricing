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

from ralph_pricing import models
from ralph_pricing.plugins.reports.base import BaseReportPlugin


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
        self.usage_type = models.UsageType(
            name='UsageType1',
            symbol='ut1',
            by_warehouse=False,
            by_cost=False,
            type='BU',
        )
        self.usage_type.save()
        self.usage_type_cost_wh = models.UsageType(
            name='UsageType2',
            symbol='ut2',
            by_warehouse=True,
            by_cost=True,
            type='BU',
        )
        self.usage_type_cost_wh.save()

        # warehouses
        self.warehouse1 = models.Warehouse(
            name='Warehouse1',
            show_in_report=True,
        )
        self.warehouse1.save()
        self.warehouse2 = models.Warehouse(
            name='Warehouse2',
            show_in_report=True,
        )
        self.warehouse2.save()
        self.warehouses = models.Warehouse.objects.all()

        # ventures
        self.venture1 = models.Venture(
            venture_id=1,
            name='V1',
            is_active=True,
        )
        self.venture1.save()
        self.venture2 = models.Venture(
            venture_id=2,
            name='V2',
            is_active=True,
        )
        self.venture2.save()
        self.venture3 = models.Venture(venture_id=3, name='V3', is_active=True)
        self.venture3.save()
        self.venture4 = models.Venture(venture_id=4, name='V4', is_active=True)
        self.venture4.save()
        self.ventures = models.Venture.objects.all()

        # daily usages of base type
        # ut1:
        #   venture1: 10
        #   venture2: 20
        # ut2:
        #   venture1: 20 (half in warehouse1, half in warehouse2)
        #   venture2: 40 (half in warehouse1, half in warehouse2)
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        base_usage_types = models.UsageType.objects.filter(type='BU')
        for i, ut in enumerate(base_usage_types, start=1):
            days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
            for j, day in enumerate(days, start=1):
                for k, venture in enumerate(self.ventures, start=1):
                    daily_usage = models.DailyUsage(
                        date=day,
                        pricing_venture=venture,
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
    # _get_price_from_cost
    # =========================================================================
    @mock.patch('ralph_pricing.plugins.reports.base.BaseReportPlugin._get_total_usage_in_period')  # noqa
    def test_get_price_from_cost(self, get_total_usage_in_period_mock):
        get_total_usage_in_period_mock.return_value = 100.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            cost=2000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(usage_price, False)

        self.assertEquals(result, D(20))  # 2000 / 100 = 20
        get_total_usage_in_period_mock.assert_called_with(
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            None,
            None,
        )

    @mock.patch('ralph_pricing.plugins.reports.base.BaseReportPlugin._get_total_usage_in_period')  # noqa
    def test_get_price_from_cost_with_warehouse(
        self,
        get_total_usage_in_period_mock
    ):
        get_total_usage_in_period_mock.return_value = 100.0
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
        get_total_usage_in_period_mock.assert_called_with(
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            self.warehouse1,
            None,
        )

    @mock.patch('ralph_pricing.plugins.reports.base.BaseReportPlugin._get_total_usage_in_period')  # noqa
    def test_get_price_from_cost_with_forecast(
        self,
        get_total_usage_in_period_mock
    ):
        get_total_usage_in_period_mock.return_value = 100.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            forecast_cost=3000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(usage_price, True)

        self.assertEquals(result, D(30))  # 3000 / 100 = 30
        get_total_usage_in_period_mock.assert_called_with(
            datetime.date(2013, 10, 10),
            datetime.date(2013, 10, 10),
            self.usage_type_cost_wh,
            None,
            None,
        )

    @mock.patch('ralph_pricing.plugins.reports.base.BaseReportPlugin._get_total_usage_in_period')  # noqa
    def test_get_price_from_cost_total_usage_0(
        self,
        get_total_usage_in_period_mock
    ):
        get_total_usage_in_period_mock.return_value = 0.0
        usage_price = models.UsagePrice(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 10),
            cost=3000,
            type=self.usage_type_cost_wh,
        )
        result = self.plugin._get_price_from_cost(usage_price, False)

        self.assertEquals(result, D(0))

    # =========================================================================
    # _get_total_usage_in_period
    # =========================================================================
    def test_get_total_usage_in_period(self):
        result = self.plugin._get_total_usage_in_period(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
        )
        # 11*(10 + 20 + 30 + 40) = 1100
        self.assertEquals(result, 1100.0)

    def test_get_total_usage_in_period_with_warehouse(self):
        result = self.plugin._get_total_usage_in_period(
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

    def test_get_total_usage_in_period_with_ventures(self):
        result = self.plugin._get_total_usage_in_period(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            ventures=[self.venture1]
        )
        # 11 * 10 = 110
        self.assertEquals(result, 110.0)

    def test_get_total_usage_in_period_with_ventures_and_warehouse(self):
        result = self.plugin._get_total_usage_in_period(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
            ventures=[self.venture2],
        )
        #  5 * 40 = 200
        # /^\
        #  |
        #  +--- every odd day between 10 and 20 (inclusive)
        self.assertEquals(result, 200.0)

    # =========================================================================
    # _get_usages_in_period_per_venture
    # =========================================================================
    def test_get_usages_in_period_per_venture(self):
        result = self.plugin._get_usages_in_period_per_venture(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
        )
        self.assertEquals(result, [
            {'usage': 110.0, 'pricing_venture': 1},  # 11 * 10 = 110
            {'usage': 220.0, 'pricing_venture': 2},  # 11 * 20 = 220
            {'usage': 330.0, 'pricing_venture': 3},  # 11 * 30 = 330
            {'usage': 440.0, 'pricing_venture': 4},  # 11 * 40 = 440
        ])

    def test_get_usages_in_period_per_venture_with_warehouse(self):
        result = self.plugin._get_usages_in_period_per_venture(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
        )
        self.assertEquals(result, [
            {'usage': 100.0, 'pricing_venture': 1},  # 5 * 20 = 100
            {'usage': 200.0, 'pricing_venture': 2},  # 5 * 40 = 200
            {'usage': 300.0, 'pricing_venture': 3},  # 5 * 60 = 300
            {'usage': 400.0, 'pricing_venture': 4},  # 5 * 80 = 400
        ])

    def test_get_usages_in_period_per_venture_with_ventures(self):
        result = self.plugin._get_usages_in_period_per_venture(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            ventures=[self.venture1],
        )
        self.assertEquals(result, [
            {'usage': 110.0, 'pricing_venture': 1},  # 11 * 10 = 110
        ])

    def test_get_usages_in_period_per_venture_with_warehouse_and_venture(self):
        result = self.plugin._get_usages_in_period_per_venture(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse2,
            ventures=[self.venture2],
        )
        self.assertEquals(result, [
            {'usage': 240.0, 'pricing_venture': 2}  # 6 * 40 = 240
        ])

    # =========================================================================
    # _distribute_costs
    # =========================================================================
    @mock.patch('ralph_pricing.plugins.reports.service.BaseReportPlugin._get_usages_in_period_per_venture')  # noqa
    @mock.patch('ralph_pricing.plugins.reports.service.BaseReportPlugin._get_total_usage_in_period')  # noqa
    def test_distribute_costs(self, total_usage_mock, usages_per_venture_mock):
        percentage = {
            self.usage_type.id: 20,
            self.usage_type_cost_wh.id: 80,
        }

        def sample_usages(
            start,
            end,
            usage_type,
            warehouse=None,
            ventures=None
        ):
            usages = {
                self.usage_type.id: [
                    {'pricing_venture': self.venture1.id, 'usage': 0},
                    {'pricing_venture': self.venture2.id, 'usage': 0},
                    {'pricing_venture': self.venture3.id, 'usage': 900},
                    {'pricing_venture': self.venture4.id, 'usage': 100},
                ],
                self.usage_type_cost_wh.id: [
                    {'pricing_venture': self.venture3.id, 'usage': 1200},
                    {'pricing_venture': self.venture4.id, 'usage': 400},
                ]
            }
            return usages[usage_type.id]

        def sample_total_usage(start, end, usage_type):
            total_usages = {
                self.usage_type.id: 1000,
                self.usage_type_cost_wh.id: 1600,
            }
            return total_usages[usage_type.id]

        usages_per_venture_mock.side_effect = sample_usages
        total_usage_mock.side_effect = sample_total_usage

        result = self.plugin._distribute_costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=self.ventures,
            cost=10000,
            percentage=percentage,
        )
        usage_type_count = 'ut_{0}_count'.format(self.usage_type.id)
        usage_type_cost = 'ut_{0}_cost'.format(self.usage_type.id)
        usage_type_cost_wh_count = 'ut_{0}_count'.format(
            self.usage_type_cost_wh.id
        )
        usage_type_cost_wh_cost = 'ut_{0}_cost'.format(
            self.usage_type_cost_wh.id
        )
        self.assertEquals(result, {
            self.venture1.id: {
                usage_type_count: 0,
                usage_type_cost: D(0),
            },
            self.venture2.id: {
                usage_type_count: 0,
                usage_type_cost: D(0),
            },
            self.venture3.id: {
                usage_type_count: 900,
                usage_type_cost: D('1800'),
                usage_type_cost_wh_count: 1200,
                usage_type_cost_wh_cost: D('6000'),
            },
            self.venture4.id: {
                usage_type_count: 100,
                usage_type_cost: D('200'),
                usage_type_cost_wh_count: 400,
                usage_type_cost_wh_cost: D('2000'),
            },
        })

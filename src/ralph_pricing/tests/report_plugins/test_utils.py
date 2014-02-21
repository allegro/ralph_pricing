# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.plugins.reports import utils


class TestUtils(TestCase):
    def setUp(self):
        # usage types
        self.usage_type = models.UsageType(
            name='UsageType1',
            symbol='ut1',
            by_warehouse=False,
            by_cost=False,
        )
        self.usage_type.save()
        self.usage_type_wh = models.UsageType(
            name='UsageType2',
            symbol='ut2',
            by_warehouse=True,
            by_cost=False,
        )
        self.usage_type_wh.save()
        self.usage_type_cost = models.UsageType(
            name='UsageType3',
            symbol='ut3',
            by_warehouse=False,
            by_cost=True,
        )
        self.usage_type_cost.save()
        self.usage_type_cost_wh = models.UsageType(
            name='UsageType4',
            symbol='ut4',
            by_warehouse=True,
            by_cost=True,
        )
        self.usage_type_cost_wh.save()

        # warehouses
        self.warehouse1 = models.Warehouse(name='Warehouse1')
        self.warehouse1.save()
        self.warehouse2 = models.Warehouse(name='Warehouse2')
        self.warehouse2.save()
        self.warehouses = models.Warehouse.objects.all()

        # ventures
        self.venture1 = models.Venture(venture_id=1, name='V1', is_active=True)
        self.venture1.save()
        self.venture2 = models.Venture(venture_id=2, name='V2', is_active=True)
        self.venture2.save()
        self.ventures = models.Venture.objects.all()

        # daily usages
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)

        for i, ut in enumerate(models.UsageType.objects.all(), start=1):
            for j, day in enumerate(rrule.rrule(rrule.DAILY, dtstart=start, until=end), start=1):
                for k, venture in enumerate(models.Venture.objects.all(), start=1):
                    # some of ventures sometimes will not have daily usages
                    if i % 4 == 0 and k % 4 == 0:
                        continue
                    daily_usage = models.DailyUsage(
                        date=day,
                        pricing_venture=venture,
                        value=100 * i * j * k,
                        type=ut,
                    )
                    if ut.by_warehouse:
                        daily_usage.warehouse = self.warehouses[j % len(self.warehouses)]
                    daily_usage.save()

        # usage prices
        dates = [
            (datetime.date(2013, 10, 5), datetime.date(2013, 10, 12)),
            (datetime.date(2013, 10, 13), datetime.date(2013, 10, 17)),
            (datetime.date(2013, 10, 18), datetime.date(2013, 10, 25)),
        ]
        ut_prices = [
            (self.usage_type, [10, 20, 30]),
            (self.usage_type_cost, [54000, 18000, 5850]),
            (self.usage_type_wh, [[44, 55, 66], [77, 88, 99]]),
            (self.usage_type_cost_wh, [
                [36000, 57600, 7800],  # warehouse1
                [500, 600, 700],  # warehouse2
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
                    usage_price.cost = price_cost
                else:
                    usage_price.price = price_cost
                usage_price.save()

        for ut, prices in ut_prices:
            if ut.by_warehouse:
                for i, prices_wh in enumerate(prices):
                    warehouse = self.warehouses[i]
                    add_usage_price(ut, prices_wh, warehouse)
            else:
                add_usage_price(ut, prices)

    def test_get_prices_from_cost(self):
        prices = utils.get_prices_from_costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost,
        )
        # usage from 5 to 12: 13500 (with cost 54000)
        # usage from 13 to 17: 36000 (with cost 18000)
        # usage from 18 to 25: 58500 (with cost 5850)
        # price from 5 to 12: 54000/13500 = 4
        # price from 13 to 17: 18000/36000 = 0.5
        # price from 18 to 25: 5850/58500 = 0.1
        self.assertEquals(prices, [
            {
                'start': datetime.date(2013, 10, 5),
                'end': datetime.date(2013, 10, 12),
                'price': D('4'),
            },
            {
                'start': datetime.date(2013, 10, 13),
                'end': datetime.date(2013, 10, 17),
                'price': D('0.5'),
            },
            {
                'start': datetime.date(2013, 10, 18),
                'end': datetime.date(2013, 10, 25),
                'price': D('0.1'),
            },
        ])

    def test_get_prices_from_cost_with_warehouse(self):
        prices = utils.get_prices_from_costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
        )
        # usage from 5 to 12: 7200 (with cost 36000)
        # usage from 13 to 17: 28800 (with cost 57600)
        # usage from 18 to 25: 31200 (with cost 7800)
        # price from 5 to 12: 36000/7200 = 5
        # price from 13 to 17: 57600/28800 = 2
        # price from 18 to 25: 7800/31200 = 0.25
        self.assertEquals(prices, [
            {
                'start': datetime.date(2013, 10, 5),
                'end': datetime.date(2013, 10, 12),
                'price': D('5'),
            },
            {
                'start': datetime.date(2013, 10, 13),
                'end': datetime.date(2013, 10, 17),
                'price': D('2'),
            },
            {
                'start': datetime.date(2013, 10, 18),
                'end': datetime.date(2013, 10, 25),
                'price': D('0.25'),
            },
        ])

    def test_get_prices_from_cost_no_usage(self):
        usage_type = models.UsageType(
            name='UsageType5',
            symbol='ut5',
            by_warehouse=False,
            by_cost=True,
        )
        usage_type.save()
        usage_price = models.UsagePrice(
            type=usage_type,
            start=datetime.date(2013, 11, 11),
            end=datetime.date(2013, 11, 15),
            cost=1234,
        )
        usage_price.save()

        prices = utils.get_prices_from_costs(
            start=datetime.date(2013, 11, 12),
            end=datetime.date(2013, 11, 14),
            usage_type=usage_type,
        )
        self.assertEquals(prices, [
            {
                'start': datetime.date(2013, 11, 11),
                'end': datetime.date(2013, 11, 15),
                'price': D('0'),
            },
        ])

    def test_get_prices_from_cost_cost_0(self):
        usage_type = models.UsageType(
            name='UsageType5',
            symbol='ut5',
            by_warehouse=False,
            by_cost=True,
        )
        usage_type.save()
        usage_price = models.UsagePrice(
            type=usage_type,
            start=datetime.date(2013, 11, 11),
            end=datetime.date(2013, 11, 15),
            cost=0,
        )
        usage_price.save()
        daily_usage = models.DailyUsage(
            date=datetime.date(2013, 11, 13),
            pricing_venture=self.venture1,
            value=100,
            type=usage_type,
        )
        daily_usage.save()

        prices = utils.get_prices_from_costs(
            start=datetime.date(2013, 11, 12),
            end=datetime.date(2013, 11, 14),
            usage_type=usage_type,
        )
        self.assertEquals(prices, [
            {
                'start': datetime.date(2013, 11, 11),
                'end': datetime.date(2013, 11, 15),
                'price': D('0'),
            },
        ])

    def test_get_prices(self):
        prices = utils.get_prices(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
        )
        self.assertEquals(len(prices), 3)
        self.assertEquals(prices[0].price, 10)
        self.assertEquals(prices[1].price, 20)
        self.assertEquals(prices[2].price, 30)

    def test_get_prices_with_warehouse(self):
        prices = utils.get_prices(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_wh,
            warehouse=self.warehouse2,
        )
        self.assertEquals(len(prices), 3)
        self.assertEquals(prices[0].price, 77)
        self.assertEquals(prices[1].price, 88)
        self.assertEquals(prices[2].price, 99)

    def test_generate_prices_list(self):
        prices = [
            utils.AttributeDict({
                'start': datetime.date(2013, 10, 5),
                'end': datetime.date(2013, 10, 12),
                'price': D('5'),
            }),
            models.UsagePrice(
                start=datetime.date(2013, 10, 13),
                end=datetime.date(2013, 10, 17),
                price=D('2'),
            ),
        ]
        prices_list = utils.generate_prices_list(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 15),
            prices=prices,
        )
        self.assertEquals(prices_list, {
            '2013-10-10': D('5'),
            '2013-10-11': D('5'),
            '2013-10-12': D('5'),
            '2013-10-13': D('2'),
            '2013-10-14': D('2'),
            '2013-10-15': D('2'),
        })

    def test_generate_prices_list_no_price(self):
        prices = [
            utils.AttributeDict({
                'start': datetime.date(2013, 10, 5),
                'end': datetime.date(2013, 10, 12),
                'price': D('5'),
            }),
        ]
        prices_list = utils.generate_prices_list(
            start=datetime.date(2013, 10, 14),
            end=datetime.date(2013, 10, 15),
            prices=prices,
        )
        self.assertEquals(prices_list, 'No Price')

    def test_generate_prices_list_incomplete_price(self):
        prices = [
            utils.AttributeDict({
                'start': datetime.date(2013, 10, 5),
                'end': datetime.date(2013, 10, 12),
                'price': D('5'),
            }),
        ]
        prices_list = utils.generate_prices_list(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 15),
            prices=prices,
        )
        self.assertEquals(prices_list, 'Incomplete Price')

    def test_get_daily_usages(self):
        daily_usages = utils.get_daily_usages(
            start=datetime.date(2013, 10, 5),
            end=datetime.date(2013, 10, 9),
            ventures=self.ventures,
            usage_type=self.usage_type,
        )
        # import ipdb; ipdb.set_trace()
        self.assertEquals([du for du in daily_usages], [
            {
                'date': datetime.datetime(2013, 10, 8, 0, 0),
                'pricing_venture': 1,
                'value': 100.0,
            },
            {
                'date': datetime.datetime(2013, 10, 8, 0, 0),
                'pricing_venture': 2,
                'value': 200.0,
            },
            {
                'date': datetime.datetime(2013, 10, 9, 0, 0),
                'pricing_venture': 1,
                'value': 200.0,
            },
            {
                'date': datetime.datetime(2013, 10, 9, 0, 0),
                'pricing_venture': 2,
                'value': 400.0,
            },
        ])

    def test_get_daily_usages_with_warehouse(self):
        daily_usages = utils.get_daily_usages(
            start=datetime.date(2013, 10, 5),
            end=datetime.date(2013, 10, 9),
            ventures=self.ventures,
            usage_type=self.usage_type_wh,
            warehouse=self.warehouse1,
        )
        self.assertEquals([du for du in daily_usages], [
            {
                'date': datetime.datetime(2013, 10, 9, 0, 0),
                'pricing_venture': 1,
                'value': 400.0,
            },
            {
                'date': datetime.datetime(2013, 10, 9, 0, 0),
                'pricing_venture': 2,
                'value': 800.0,
            },
        ])

    def test_prepare_data(self):
        daily_usages = [
            {
                'date': datetime.datetime(2013, 10, 8, 0, 0),
                'pricing_venture': 1,
                'value': 100.0,
            },
            {
                'date': datetime.datetime(2013, 10, 8, 0, 0),
                'pricing_venture': 2,
                'value': 200.0,
            },
            {
                'date': datetime.datetime(2013, 10, 9, 0, 0),
                'pricing_venture': 1,
                'value': 200.0,
            },
            {
                'date': datetime.datetime(2013, 10, 9, 0, 0),
                'pricing_venture': 2,
                'value': 400.0,
            },
            {
                'date': datetime.datetime(2013, 10, 10, 0, 0),
                'pricing_venture': 2,
                'value': 990.0,
            },
        ]
        prices_list = {
            '2013-10-07': D('5'),
            '2013-10-08': D('3'),
            '2013-10-09': D('2'),
            '2013-10-10': D('10'),
            '2013-10-11': D('9'),
        }
        total_costs = utils.prepare_data(daily_usages, prices_list)
        self.assertEquals(total_costs, {
            1: {
                'value': 300.0,
                'cost': D('700'),
            },
            2: {
                'value': 1590.0,
                'cost': D('11300'),
            },
        })

    def test_get_usages_and_costs(self):
        usages_and_costs = utils.get_usages_and_costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=self.ventures,
            usage_type=self.usage_type_cost,
        )
        self.assertEquals(usages_and_costs, {
            1: {
                'value': 26400.0,
                'cost': D('21480.0'),
            },
            2: {
                'value': 52800.0,
                'cost': D('42960.0'),
            },
        })

    def test_get_usages_and_costs_with_warehouse(self):
        usages_and_costs = utils.get_usages_and_costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=self.ventures,
            usage_type=self.usage_type_cost_wh,
            warehouse=self.warehouse1,
        )
        self.assertEquals(usages_and_costs, {
            1: {
                'value': 16000.0,
                'cost': D('28400.0'),
            },
            2: {
                'value': 32000.0,
                'cost': D('56800.0'),
            },
        })

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from collections import OrderedDict
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ralph_scrooge import models
from ralph_scrooge.plugins.reports.usage import UsagePlugin
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    ServiceFactory,
    UsageTypeFactory,
    WarehouseFactory,
    DailyPricingObjectFactory,
)


class TestUsageBasePlugin(TestCase):
    def setUp(self):
        # usage types
        self.usage_type = UsageTypeFactory(
            symbol='ut1',
            by_warehouse=False,
            by_cost=False,
            type='BU',
            divide_by=1,
        )
        self.usage_type_cost_wh = UsageTypeFactory(
            symbol='ut2',
            by_warehouse=True,
            by_cost=True,
            type='BU',
            rounding=2,
        )
        self.usage_type_cost_sum = UsageTypeFactory(
            symbol='ut3',
            by_warehouse=False,
            by_cost=True,
            type='BU',
            by_internet_provider=True,
            rounding=1,
        )
        self.usage_type_average = UsageTypeFactory(
            symbol='ut4',
            by_warehouse=False,
            by_cost=False,
            type='BU',
            average=True,
            divide_by=2,
        )

        # warehouses
        self.default_warehouse = models.Warehouse.objects.get(name='Default')
        self.warehouse1 = WarehouseFactory(name='WH1', show_in_report=True)
        self.warehouse2 = WarehouseFactory(name='WH2', show_in_report=True)
        self.warehouses = models.Warehouse.objects.exclude(
            pk=self.default_warehouse.pk
        )

        # internet providers
        self.net_provider1 = models.InternetProvider(
            name='InternetProvider1',
        )
        self.net_provider1.save()
        self.net_provider2 = models.InternetProvider(
            name='InternetProvider2',
        )
        self.net_provider2.save()
        self.net_providers = models.InternetProvider.objects.all()

        # services
        self.service1 = ServiceFactory()
        self.service2 = ServiceFactory()
        self.service3 = ServiceFactory()
        self.service4 = ServiceFactory()
        self.services_subset = [self.service1, self.service2]
        self.services = models.Service.objects.all()

        # daily usages of base type
        # ut1:
        #   service1: 10
        #   service2: 20
        # ut2:
        #   service1: 20 (half in warehouse1, half in warehouse2)
        #   service2: 40 (half in warehouse1, half in warehouse2)
        # ut3:
        #   service1: 30
        #   service2: 60
        # ut4:
        #   service1: 40
        #   service2: 80
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        base_usage_types = models.UsageType.objects.filter(type='BU')
        self.services_pricing_objects = {}
        for k, service in enumerate(self.services, start=1):
            daily_pricing_object = DailyPricingObjectFactory()
            self.services_pricing_objects[service] = (
                daily_pricing_object.pricing_object
            )
            for i, ut in enumerate(base_usage_types, start=1):
                days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
                for j, day in enumerate(days, start=1):
                    daily_usage = models.DailyUsage(
                        date=day,
                        service=service,
                        daily_pricing_object=daily_pricing_object,
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
            (self.usage_type_cost_sum, [
                [(1000, 2000), (2000, 3000), (4000, 5000)],  # provider 1
                [(10000, 20000), (20000, 30000), (40000, 50000)],  # provider 2
            ]),
            (self.usage_type_average, [(10, 20), (20, 30), (30, 40)]),
        ]

        def add_usage_price(
            usage_type,
            prices_costs,
            net_provider=None,
            warehouse=None
        ):
            for daterange, price_cost in zip(dates, prices_costs):
                start, end = daterange
                usage_price = models.UsagePrice(
                    type=usage_type,
                    start=start,
                    end=end,
                )
                if warehouse is not None:
                    usage_price.warehouse = warehouse
                if net_provider is not None:
                    usage_price.internet_provider = net_provider
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
                    add_usage_price(ut, prices_wh, warehouse=warehouse)
            elif ut.by_internet_provider:
                for i, prices_ip in enumerate(prices):
                    net_provider = self.net_providers[i]
                    add_usage_price(ut, prices_ip, net_provider=net_provider)
            else:
                add_usage_price(ut, prices)

    def test_incomplete_price(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
        )
        self.assertEquals(result, None)

    def test_incomplete_price_by_warehouse(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type_cost_wh,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            warehouse=self.warehouse1,
        )
        self.assertEquals(result, None)

    def test_incomplete_price_no_price(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type,
            start=datetime.date(2013, 11, 10),
            end=datetime.date(2013, 11, 20),
        )
        self.assertEquals(result, 'No price')

    def test_incomplete_price_incomplete_price(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 11, 20),
        )
        self.assertEquals(result, 'Incomplete price')

    def test_incomplete_price_internet_providers(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type_cost_sum,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
        )
        self.assertEquals(result, None)

    def test_incomplete_price_internet_providers_incomplete_price(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type_cost_sum,
            start=datetime.date(2013, 10, 4),
            end=datetime.date(2013, 10, 25),
        )
        self.assertEquals(result, 'Incomplete price')

    def test_incomplete_price_internet_providers_incomplete_price2(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type_cost_sum,
            start=datetime.date(2013, 10, 3),
            end=datetime.date(2013, 10, 28),
        )
        self.assertEquals(result, 'Incomplete price')

    def test_incomplete_price_internet_providers_no_price(self):
        result = UsagePlugin._incomplete_price(
            usage_type=self.usage_type_cost_sum,
            start=datetime.date(2013, 10, 26),
            end=datetime.date(2013, 11, 20),
        )
        self.assertEquals(result, 'No price')

    def test_get_usage_type_cost(self):
        result = UsagePlugin._get_total_cost_by_warehouses(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            services=self.services_subset,
            forecast=False,
        )
        # 10-12: usage: 3 * (10 + 20) = 90; cost: 90 * 10 = 900
        # 13-17: usage: 5 * (10 + 20) = 150; cost: 150 * 20 = 3000
        # 18-20: usage: 3 * (10 + 20) = 90; cost = 90 * 30 = 2700
        # total: usage: 330; cost: 6600
        self.assertEquals(result, [330.0, D('6600')])

    def test_get_total_cost(self):
        result = UsagePlugin.total_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            services=self.services_subset,
            forecast=False,
        )
        self.assertEquals(result, D('6600'))

    def test_get_usage_type_cost_forecast(self):
        result = UsagePlugin._get_total_cost_by_warehouses(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            services=[self.service1],
            forecast=True,
        )
        # 10-12: usage: 3 * 10 = 30; cost: 30 * 50 = 1500
        # 13-17: usage: 5 * 10 = 50; cost: 50 * 60 = 3000
        # 18-20: usage: 3 * 10 = 30; cost = 30 * 70 = 2100
        # total: usage: 110; cost: 6600
        self.assertEquals(result, [110.0, D('6600')])

    def test_get_usage_type_cost_by_cost(self):
        result = UsagePlugin._get_total_cost_by_warehouses(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            services=self.services_subset,
            forecast=False,
        )
        # 5-12: (usages are from 8 to 12)
        #   warehouse1:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 3600;
        #               price = 3600 / 400 = 9;
        #   warehouse2:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 3600;
        #               price = 3600 / 600 = 6;
        # 13-17:
        #   warehouse1:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 5400
        #               price = 5400 / 600 = 9;
        #   warehouse2:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 3600
        #               price = 3600 / 400 = 9;
        # 18-25: (usages are from 18 to 22)
        #   warehouse1:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 4800
        #               price = 4800 / 400 = 12;
        #   warehouse2:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 7200
        #               price = 7200 / 600 = 12;

        # 10-12:
        #   warehouse1: usage: 1 * (20 + 40) = 60;
        #               cost: 60 * 9 = 540
        #   warehouse2: usage: 2 * (20 + 40) = 120;
        #               cost: 120 * 6 = 720
        # 13-17:
        #   warehouse1: usage: 3 * (20 + 40) = 180;
        #               cost: 180 * 9 = 1620
        #   warehouse2: usage: 2 * (20 + 40) = 120;
        #               cost: 120 * 9 = 1080
        # 18-20:
        #   warehouse1: usage: 1 * (20 + 40) = 60;
        #               cost: 60 * 12 = 720
        #   warehouse2: usage: 2 * (20 + 40) = 120;
        #               cost: 120 * 12 = 1440
        # total:
        #   warehouse1: usage: 300; cost: 2880
        #   warehouse2: usage: 360; cost: 3240
        #   total: cost: 6840
        self.assertEquals(
            result,
            [300.0, D('2880'), 360.0, D('3240'), D('6120')]
        )

    def test_get_usage_type_cost_by_cost_forecast(self):
        result = UsagePlugin._get_total_cost_by_warehouses(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            services=[self.service1],
            forecast=True,
        )
        # 5-12: (usages are from 8 to 12)
        #   warehouse1:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 2400;
        #               price = 2400 / 400 = 6;
        #   warehouse2:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 5400;
        #               price = 5400 / 600 = 9;
        # 13-17:
        #   warehouse1:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 5400
        #               price = 5400 / 600 = 9;
        #   warehouse2:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 1200
        #               price = 1200 / 400 = 3;
        # 18-25: (usages are from 18 to 22)
        #   warehouse1:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 12000
        #               price = 12000 / 400 = 30;
        #   warehouse2:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 3600
        #               price = 3600 / 600 = 6;

        # 10-12:
        #   warehouse1: usage: 1 * 20 = 20;
        #               cost: 20 * 6 = 120
        #   warehouse2: usage: 2 * 20 = 40;
        #               cost: 40 * 9 = 360
        # 13-17:
        #   warehouse1: usage: 3 * 20 = 60;
        #               cost: 60 * 9 = 540
        #   warehouse2: usage: 2 * 20 = 40;
        #               cost: 40 * 3 = 120
        # 18-20:
        #   warehouse1: usage: 1 * 20 = 20;
        #               cost: 20 * 30 = 600
        #   warehouse2: usage: 2 * 20 = 40;
        #               cost: 40 * 6 = 240
        # total:
        #   warehouse1: usage: 100; cost: 1260
        #   warehouse2: usage: 120; cost: 720
        #   total: cost: 1980
        self.assertEquals(
            result,
            [100.0, D('1260'), 120.0, D('720'), D('1980')]
        )

    def test_get_usage_type_cost_sum(self):
        result = UsagePlugin._get_total_cost_by_warehouses(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_sum,
            services=self.services_subset,
            forecast=False,
        )
        # 5-12: (usages are from 8 to 12)
        #   usage: 5 * (30 + 60 + 90 + 120) = 1500;
        #   cost: 1000 + 10000 = 11000;
        #   price = 11000 / 1500 = 7.(3);
        # 13-17:
        #   usage: 5 * (30 + 60) = 1500;
        #   cost: 2000 + 20000 = 22000;
        #   price = 22000 / 1500 = 14.(6);
        # 18-25: (usages are from 18 to 22)
        #   usage: 5 * (30 + 60) = 1500;
        #   cost: 4000 + 40000 = 44000;
        #   price = 11000 / 1500 = 29.(3);
        #
        # 10-12:
        #   usage: 3 * (30 + 60) = 270;
        #   cost: 270 * 7.(3) = 1980
        # 13-17:
        #   usage: 5 * (30 + 60) = 450;
        #   cost: 450 * 14.(6) = 6600
        # 18-20:
        #   usage: 3 * (30 + 60) = 270;
        #   cost: 270 * 29.(3) = 7920
        #
        # total cost: 1980 + 6600 + 7920 = 16500
        self.assertEquals(result, [990.0, D('16500')])

    def test_get_total_cost_sum(self):
        result = UsagePlugin.total_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_sum,
            services=self.services_subset,
            forecast=False,
        )
        self.assertEquals(result, D('16500'))

    def test_get_total_cost_sum_whole(self):
        result = UsagePlugin.total_cost(
            start=datetime.date(2013, 10, 5),
            end=datetime.date(2013, 10, 25),
            usage_type=self.usage_type_cost_sum,
            services=self.services,
            forecast=False,
        )
        self.assertEquals(result, D('77000'))

    def test_get_total_cost_sum_beyond_usageprices(self):
        # even with no_price_msg total cost should return valid cost
        result = UsagePlugin.total_cost(
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 28),
            usage_type=self.usage_type_cost_sum,
            services=self.services,
            forecast=False,
            no_price_msg=True,
        )
        self.assertEquals(result, D('77000'))

    def test_get_usage_type_cost_sum_forecast(self):
        result = UsagePlugin._get_total_cost_by_warehouses(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_sum,
            services=[self.service1],
            forecast=True,
        )
        # 5-12: (usages are from 8 to 12)
        #   usage: 5 * (30 + 60 + 90 + 120) = 1500;
        #   cost: 2000 + 20000 = 22000;
        #   price = 22000 / 1500 = 14.(6);
        # 13-17:
        #   usage: 5 * (30 + 60) = 1500;
        #   cost: 3000 + 30000 = 33000;
        #   price = 33000 / 1500 = 22;
        # 18-25: (usages are from 18 to 22)
        #   usage: 5 * (30 + 60) = 1500;
        #   cost: 5000 + 50000 = 55000;
        #   price = 55000 / 1500 = 36.(6);
        #
        # 10-12: usage: 3 * 30 = 90; cost: 90 * 14.(6) = 1320
        # 13-17: usage: 5 * 30 = 150; cost: 150 * 22 = 3300
        # 18-20: usage: 3 * 30 = 90; cost = 90 * 36.(6) = 3300
        # total: usage: 330; cost: 7920
        self.assertEquals(result, [330.0, D('7920')])

    def test_get_usages(self):
        result = UsagePlugin.costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            services=self.services_subset,
            forecast=False,
            no_price_msg=False,
        )
        count_key = 'ut_{}_count'.format(self.usage_type.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type.id)
        self.assertEquals(result, {
            1: {
                count_key: 110.0,  # 11 * 10
                cost_key: D('2200'),  # 10 * (3 * 10 + 5 * 20 + 3 * 30)
            },
            2: {
                count_key: 220.0,  # 11 * 20
                cost_key: D('4400'),  # 20 * (3 * 10 + 5 * 20 + 3 * 30)
            }
        })

    def test_get_usages_incomplete_price(self):
        result = UsagePlugin.costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 30),
            usage_type=self.usage_type,
            services=self.services_subset,
            forecast=False,
            no_price_msg=True,
        )
        count_key = 'ut_{}_count'.format(self.usage_type.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type.id)
        self.assertEquals(result, {
            1: {
                count_key: 130.0,  # 13 * 10
                cost_key: _('Incomplete price'),
            },
            2: {
                count_key: 260.0,  # 13 * 20
                cost_key: _('Incomplete price'),
            }
        })

    def test_get_usages_no_price(self):
        start = datetime.date(2013, 11, 8)
        end = datetime.date(2013, 11, 22)
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
                        warehouse=self.default_warehouse
                    )
                    if ut.by_warehouse:
                        daily_usage.warehouse = (
                            self.warehouses[j % len(self.warehouses)]
                        )
                    daily_usage.save()
        result = UsagePlugin.costs(
            start=datetime.date(2013, 11, 10),
            end=datetime.date(2013, 11, 20),
            usage_type=self.usage_type,
            services=self.services_subset,
            forecast=False,
            no_price_msg=True,
        )
        count_key = 'ut_{}_count'.format(self.usage_type.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type.id)
        self.assertEquals(result, {
            1: {
                count_key: 110.0,  # 11 * 10
                cost_key: _('No price'),
            },
            2: {
                count_key: 220.0,  # 11 * 20
                cost_key: _('No price'),
            }
        })

    def test_get_usages_per_warehouse_with_warehouse(self):
        result = UsagePlugin._get_usages_per_warehouse(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            services=self.services_subset,
            forecast=False,
        )
        # prices:
        # 5-12: (usages are from 8 to 12)
        #   warehouse1:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 3600;
        #               price = 3600 / 400 = 9;
        #   warehouse2:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 3600;
        #               price = 3600 / 600 = 6;
        # 13-17:
        #   warehouse1:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 5400
        #               price = 5400 / 600 = 9;
        #   warehouse2:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 3600
        #               price = 3600 / 400 = 9;
        # 18-25: (usages are from 18 to 22)
        #   warehouse1:
        #               usage: 2 * (20 + 40 + 60 + 80) = 400;
        #               cost: 4800
        #               price = 4800 / 400 = 12;
        #   warehouse2:
        #               usage: 3 * (20 + 40 + 60 + 80) = 600;
        #               cost: 7200
        #               price = 7200 / 600 = 12;

        # warehouse1 has usages only in odd days
        # odd days in usages prices:
        # 10-12: 1
        # 13-17: 3
        # 18-20: 1

        # warehouse2 has usages only in even days
        # even days in usages prices:
        # 10-12: 2
        # 13-17: 2
        # 18-20: 2
        ut_key = 'ut_{}_'.format(self.usage_type_cost_wh.id)
        count_wh1_key = '{}count_wh_{}'.format(ut_key, self.warehouse1.id)
        cost_wh1_key = '{}cost_wh_{}'.format(ut_key, self.warehouse1.id)
        count_wh2_key = '{}count_wh_{}'.format(ut_key, self.warehouse2.id)
        cost_wh2_key = '{}cost_wh_{}'.format(ut_key, self.warehouse2.id)
        total_cost_key = '{}total_cost'.format(ut_key)
        self.assertEquals(result, {
            1: {
                count_wh1_key: 100.0,  # 5 * 20 (5 is number of odd days)
                cost_wh1_key: D('960'),  # 20 * (1 * 9 + 3 * 9 + 1 * 12)
                count_wh2_key: 120.0,  # 6 * 20 (6 is number of even days)
                cost_wh2_key: D('1080'),  # 20 * (2 * 6 + 2 * 9 + 2 * 12)
                total_cost_key: D('2040'),  # 960 + 1080
            },
            2: {
                count_wh1_key: 200.0,  # 5 * 40 (5 is number of odd days)
                cost_wh1_key: D('1920'),  # 40 * (1 * 9 + 3 * 9 + 1 * 12)
                count_wh2_key: 240.0,  # 6 * 40 (6 is number of even days)
                cost_wh2_key: D('2160'),  # 40 * (2 * 6 + 2 * 9 + 2 * 12)
                total_cost_key: D('4080'),  # 1920 + 2160
            },
        })

    def test_get_usages_per_warehouse_by_device(self):
        result = UsagePlugin._get_usages_per_warehouse(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_wh,
            services=[self.service1],
            forecast=False,
            by_device=True,
        )
        ut_key = 'ut_{}_'.format(self.usage_type_cost_wh.id)
        count_wh1_key = '{}count_wh_{}'.format(ut_key, self.warehouse1.id)
        cost_wh1_key = '{}cost_wh_{}'.format(ut_key, self.warehouse1.id)
        count_wh2_key = '{}count_wh_{}'.format(ut_key, self.warehouse2.id)
        cost_wh2_key = '{}cost_wh_{}'.format(ut_key, self.warehouse2.id)
        total_cost_key = '{}total_cost'.format(ut_key)
        self.assertEquals(result, {
            self.services_pricing_objects[self.service1].id: {
                count_wh1_key: 100.0,  # 5 * 20 (5 is number of odd days)
                cost_wh1_key: D('960'),  # 20 * (1 * 9 + 3 * 9 + 1 * 12)
                count_wh2_key: 120.0,  # 6 * 20 (6 is number of even days)
                cost_wh2_key: D('1080'),  # 20 * (2 * 6 + 2 * 9 + 2 * 12)
                total_cost_key: D('2040'),  # 960 + 1080
            }
        })

    def test_usage_type_average(self):
        result = UsagePlugin.costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_average,
            services=self.services_subset,
            forecast=False,
        )
        count_key = 'ut_{}_count'.format(self.usage_type_average.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type_average.id)
        self.assertEquals(result, {
            1: {
                count_key: 40.0,  # average daily usage
                cost_key: D('8800'),
            },
            2: {
                count_key: 80.0,  # average daily usage
                cost_key: D('17600'),
            },
        })

    def test_usage_type_average_without_average(self):
        result = UsagePlugin.costs(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_average,
            services=self.services_subset,
            forecast=False,
            use_average=False,
        )
        count_key = 'ut_{}_count'.format(self.usage_type_average.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type_average.id)
        self.assertEquals(result, {
            1: {
                count_key: 440.0,  # sum of daily usage
                cost_key: D('8800'),
            },
            2: {
                count_key: 880.0,  # sum of daily usage
                cost_key: D('17600'),
            },
        })

    def test_get_usages_by_internet_provider(self):
        result = UsagePlugin._get_usages_per_warehouse(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type_cost_sum,
            services=self.services_subset,
            forecast=False,
        )
        # 5-12: (usages are from 8 to 12)
        #   usage: 5 * (30 + 60 + 90 + 120) = 1500;
        #   cost: 1000 + 10000 = 11000;
        #   price = 11000 / 1500 = 7.(3);
        # 13-17:
        #   usage: 5 * (30 + 60 + 90 + 120) = 1500;
        #   cost: 2000 + 20000 = 22000;
        #   price = 22000 / 1500 = 14.(6);
        # 18-25: (usages are from 18 to 22)
        #   usage: 5 * (30 + 60 + 90 + 120) = 1500;
        #   cost: 4000 + 40000 = 44000;
        #   price = 44000 / 1500 = 29.(3);
        count_key = 'ut_{}_count'.format(self.usage_type_cost_sum.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type_cost_sum.id)
        self.assertEquals(result, {
            1: {
                count_key: 330.0,  # 3 * 30 + 5 * 30 + 3 * 30
                cost_key: D('5500'),  # 90*7.(3) + 150*14.(6) + 90*29.(3)
            },
            2: {
                count_key: 660.0,  # 3 * 60 + 5 * 60 + 3 * 60
                cost_key: D('11000'),  # 180*7.(3) + 300*14.(6) + 180*29.(3)
            },
        })

    def test_get_usages_by_internet_provider_incomplete_price(self):
        result = UsagePlugin._get_usages_per_warehouse(
            start=datetime.date(2013, 10, 4),
            end=datetime.date(2013, 10, 26),
            usage_type=self.usage_type_cost_sum,
            services=self.services_subset,
            forecast=False,
            no_price_msg=True,
        )
        count_key = 'ut_{}_count'.format(self.usage_type_cost_sum.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type_cost_sum.id)
        self.assertEquals(result, {
            1: {
                count_key: 450.0,  # 5 * 30 + 5 * 30 + 5 * 30
                cost_key: 'Incomplete price',
            },
            2: {
                count_key: 900.0,  # 5 * 60 + 5 * 60 + 5 * 60
                cost_key: 'Incomplete price',
            },
        })

    def test_get_dailyusages(self):
        # test if sum of usages per day is properly calculated
        DailyUsageFactory(
            date=datetime.date(2013, 10, 11),
            service=self.service2,
            value=100,
            type=self.usage_type,
        )
        result = UsagePlugin(
            usage_type=self.usage_type,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 13),
            services=self.services_subset,
            type='dailyusages',
        )
        self.assertEquals(result, {
            datetime.date(2013, 10, 10): {
                self.service1.id: 10,
                self.service2.id: 20,
            },
            datetime.date(2013, 10, 11): {
                self.service1.id: 10,
                self.service2.id: 120,  # additional usage!
            },
            datetime.date(2013, 10, 12): {
                self.service1.id: 10,
                self.service2.id: 20,
            },
            datetime.date(2013, 10, 13): {
                self.service1.id: 10,
                self.service2.id: 20,
            },
        })

    def test_schema(self):
        result = UsagePlugin(
            usage_type=self.usage_type,
            type='schema'
        )
        count_key = 'ut_{}_count'.format(self.usage_type.id)
        cost_key = 'ut_{}_cost'.format(self.usage_type.id)
        self.assertEquals(result, OrderedDict([
            (count_key, {
                'name': _('{} count'.format(self.usage_type.name)),
                'rounding': 0,
                'divide_by': 1,
            }),
            (cost_key, {
                'name': _('{} cost'.format(self.usage_type.name)),
                'currency': True,
                'total_cost': True,
            }),
        ]))

    def test_schema_with_warehouse(self):
        result = UsagePlugin(
            usage_type=self.usage_type_cost_wh,
            type='schema'
        )
        ut_key = 'ut_{}_'.format(self.usage_type_cost_wh.id)
        count_wh1_key = '{}count_wh_{}'.format(ut_key, self.warehouse1.id)
        cost_wh1_key = '{}cost_wh_{}'.format(ut_key, self.warehouse1.id)
        count_wh2_key = '{}count_wh_{}'.format(ut_key, self.warehouse2.id)
        cost_wh2_key = '{}cost_wh_{}'.format(ut_key, self.warehouse2.id)
        total_cost_key = '{}total_cost'.format(ut_key)
        self.assertEquals(result, OrderedDict([
            (count_wh1_key, {
                'name': _('{} count ({})'.format(
                    self.usage_type_cost_wh.name,
                    self.warehouse1.name
                )),
                'rounding': 2,
                'divide_by': 0,
            }),
            (cost_wh1_key, {
                'name': _('{} cost ({})'.format(
                    self.usage_type_cost_wh.name,
                    self.warehouse1.name
                )),
                'currency': True,
            }),
            (count_wh2_key, {
                'name': _('{} count ({})'.format(
                    self.usage_type_cost_wh.name,
                    self.warehouse2.name
                )),
                'rounding': 2,
                'divide_by': 0,
            }),
            (cost_wh2_key, {
                'name': _('{} cost ({})'.format(
                    self.usage_type_cost_wh.name,
                    self.warehouse2.name
                )),
                'currency': True,
            }),
            (total_cost_key, {
                'name': _('{} total cost'.format(
                    self.usage_type_cost_wh.name
                )),
                'currency': True,
                'total_cost': True,
            }),
        ]))

    def test_usages_schema(self):
        result = UsagePlugin(
            usage_type=self.usage_type_cost_wh,
            type='dailyusages_header'
        )
        self.assertEquals(result, self.usage_type_cost_wh.name)

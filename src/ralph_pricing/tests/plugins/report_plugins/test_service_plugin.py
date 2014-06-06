
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
from collections import OrderedDict
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ralph_pricing import models
from ralph_pricing.plugins.reports.service import ServicePlugin


class TestServicePlugin(TestCase):
    def setUp(self):
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

        self.service_usage_type1 = models.UsageType(
            name='ServiceUsageType1',
            symbol='sut1',
            type='SU',
        )
        self.service_usage_type1.save()
        self.service_usage_type2 = models.UsageType(
            name='ServiceUsageType2',
            # symbol='sut2',
            type='SU',
        )
        self.service_usage_type2.save()

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

        # service
        self.service = models.Service(
            name='Service1'
        )
        self.service.save()
        self.service.base_usage_types.add(
            self.usage_type_cost_wh,
            self.usage_type
        )
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type1,
            service=self.service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 15),
            percent=30,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type2,
            service=self.service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 15),
            percent=70,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type1,
            service=self.service,
            start=datetime.date(2013, 10, 16),
            end=datetime.date(2013, 10, 30),
            percent=40,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type2,
            service=self.service,
            start=datetime.date(2013, 10, 16),
            end=datetime.date(2013, 10, 30),
            percent=60,
        ).save()
        self.service.save()

        # ventures
        self.venture1 = models.Venture(
            venture_id=1,
            name='V1',
            is_active=True,
            service=self.service,  # venture is providing service
        )
        self.venture1.save()
        self.venture2 = models.Venture(
            venture_id=2,
            name='V2',
            is_active=True,
            service=self.service,  # venture is providing service
        )
        self.venture2.save()
        self.venture3 = models.Venture(venture_id=3, name='V3', is_active=True)
        self.venture3.save()
        self.venture4 = models.Venture(venture_id=4, name='V4', is_active=True)
        self.venture4.save()
        self.service_ventures = list(self.service.venture_set.all())
        self.not_service_ventures = list(
            models.Venture.objects.exclude(
                id__in=[i.id for i in self.service_ventures]
            )
        )
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

        # usage of service resources
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        service_usage_types = models.UsageType.objects.filter(type='SU')
        for i, ut in enumerate(service_usage_types, start=1):
            days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
            for j, day in enumerate(days, start=1):
                for k, venture in enumerate(
                    self.not_service_ventures,
                    start=1
                ):
                    daily_usage = models.DailyUsage(
                        date=day,
                        pricing_venture=venture,
                        value=10 * i * k,
                        type=ut,
                    )
                    daily_usage.save()

        self.maxDiff = None

    # =========================================================================
    # _get_usage_type_cost
    # =========================================================================
    @mock.patch('ralph.util.plugin.run')
    def test_get_usage_type_cost(self, plugin_run_mock):
        plugin_run_mock.return_value = 100
        result = ServicePlugin._get_usage_type_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            forecast=True,
            ventures=self.ventures,
        )
        self.assertEquals(result, 100)
        plugin_run_mock.assert_called_with(
            'reports',
            self.usage_type.get_plugin_name(),
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            forecast=True,
            ventures=self.ventures,
            type='total_cost',
        )

    @mock.patch('ralph.util.plugin.run')
    def test_get_usage_type_cost_with_exception(self, plugin_run_mock):
        for exc in (KeyError(), AttributeError()):
            plugin_run_mock.side_effect = exc
            result = ServicePlugin._get_usage_type_cost(
                start=datetime.date(2013, 10, 10),
                end=datetime.date(2013, 10, 20),
                usage_type=self.usage_type,
                forecast=True,
                ventures=self.ventures,
            )
            self.assertEquals(result, 0)

    def test_get_date_ranges_percentage(self):
        result = ServicePlugin._get_date_ranges_percentage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            service=self.service,
        )
        self.assertEquals(result, {
            (datetime.date(2013, 10, 10), datetime.date(2013, 10, 15)): {
                3: 30.0,
                4: 70.0,
            },
            (datetime.date(2013, 10, 16), datetime.date(2013, 10, 20)): {
                3: 40.0,
                4: 60.0,
            },
        })

    def test_get_date_ranges_percentage2(self):
        self.service = models.Service(
            name='Service2'
        )
        self.service.save()
        self.service.base_usage_types.add(
            self.usage_type_cost_wh,
            self.usage_type
        )
        self.service_usage_type3 = models.UsageType(
            name='ServiceUsageType3',
            symbol='sut3',
            type='SU',
        )
        self.service_usage_type3.save()

        # |__________||____|
        # |____||____||____|
        # |____||__________|
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type1,
            service=self.service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 20),
            percent=50,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type2,
            service=self.service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 10),
            percent=30,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type3,
            service=self.service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 10),
            percent=20,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type2,
            service=self.service,
            start=datetime.date(2013, 10, 11),
            end=datetime.date(2013, 10, 20),
            percent=10,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type3,
            service=self.service,
            start=datetime.date(2013, 10, 11),
            end=datetime.date(2013, 10, 30),
            percent=40,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type1,
            service=self.service,
            start=datetime.date(2013, 10, 21),
            end=datetime.date(2013, 10, 30),
            percent=30,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.service_usage_type2,
            service=self.service,
            start=datetime.date(2013, 10, 21),
            end=datetime.date(2013, 10, 30),
            percent=30,
        ).save()
        self.service.save()

        result = ServicePlugin._get_date_ranges_percentage(
            start=datetime.date(2013, 10, 5),
            end=datetime.date(2013, 10, 25),
            service=self.service,
        )

        self.assertEquals(result, {
            (datetime.date(2013, 10, 5), datetime.date(2013, 10, 10)): {
                3: 50.0,
                4: 30.0,
                5: 20.0,
            },
            (datetime.date(2013, 10, 11), datetime.date(2013, 10, 20)): {
                3: 50.0,
                4: 10.0,
                5: 40.0,
            },
            (datetime.date(2013, 10, 21), datetime.date(2013, 10, 25)): {
                3: 30.0,
                4: 30.0,
                5: 40.0,
            },
        })

    @mock.patch('ralph.util.plugin.run')
    def test_get_service_extra_cost(self, plugin_run_mock):
        plugin_run_mock.side_effect = [122]
        self.assertEqual(
            122,
            ServicePlugin._get_service_extra_cost(
                datetime.date(2013, 10, 10),
                datetime.date(2013, 10, 20),
                [self.venture1]
            )
        )
        plugin_run_mock.side_effect = KeyError()
        self.assertEqual(
            D(0),
            ServicePlugin._get_service_extra_cost(
                datetime.date(2013, 10, 10),
                datetime.date(2013, 10, 20),
                [self.venture1]
            )
        )

    def test_get_service_base_usage_types_cost(self):
        result = ServicePlugin._get_service_base_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            service=self.service,
            forecast=False,
            ventures=self.service_ventures,
        )
        # aggregate from test_get_usage_type_cost_by_cost and
        # test_get_usage_type_cost
        self.assertEquals(result, D('12720'))

    def test_get_service_base_usage_types_cost_forecast(self):
        result = ServicePlugin._get_service_base_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            service=self.service,
            forecast=True,
            ventures=[self.venture1],
        )
        # aggregate from test_get_usage_type_cost_by_cost_forecast and
        # test_get_usage_type_cost_forecast
        self.assertEquals(result, D('8580'))

    @mock.patch('ralph.util.plugin.run')
    def test_get_dependent_services_cost(self, plugin_run_mock):
        dependent_service1 = models.Service(
            name='Service2'
        )
        dependent_service1.save()
        dependent_service2 = models.Service(
            name='Service3',
            use_universal_plugin=False,
        )
        dependent_service2.save()
        self.service.dependency.add(dependent_service1, dependent_service2)
        self.service.save()

        def pl(chain, func_name, type, service, **kwargs):
            data = {
                'Service2_schema': {
                    'sut_1_count': {},
                    'sut_1_cost': {'total_cost': False},
                    'sut_2_count': {},
                    'sut_2_cost': {'total_cost': False, 'currency': True},
                    '2_service_cost': {'total_cost': True, 'currency': True},
                },
                'Service2_costs': {
                    1: {
                        'sut_1_count': 10,
                        'sut_1_cost': D(100),
                        '2_service_cost': D(100),
                    },
                    2: {
                        'sut_1_count': 10,
                        'sut_1_cost': D(100),
                        'sut_2_count': 10,
                        'sut_2_cost': D(200),
                        '2_service_cost': D(300),
                    }
                },
                'Service3_schema': {
                    'sut_1_count': {},
                    'sut_1_cost': {'total_cost': True, 'currency': True},
                },
                'Service3_costs': {
                    1: {
                        'sut_1_count': 10,
                        'sut_1_cost': D(300),
                    },
                    2: {
                        'sut_1_count': 10,
                        'sut_1_cost': D(500),
                    }
                },
            }
            key = "{0}_{1}".format(service.name, type)
            return data[key]

        plugin_run_mock.side_effect = pl

        start = datetime.date(2013, 10, 10)
        end = datetime.date(2013, 10, 20)
        forecast = True
        result = ServicePlugin._get_dependent_services_cost(
            start=start,
            end=end,
            service=self.service,
            forecast=forecast,
            ventures=self.service_ventures,
        )
        self.assertEquals(result, 1200)
        plugin_run_mock.assert_any_call(
            'reports',
            'service_plugin',
            service=dependent_service1,
            ventures=self.service_ventures,
            start=start,
            end=end,
            forecast=forecast,
            type='costs',
        )
        plugin_run_mock.assert_any_call(
            'reports',
            'service3',
            service=dependent_service2,
            ventures=self.service_ventures,
            start=start,
            end=end,
            forecast=forecast,
            type='costs',
        )

    def test_usage(self):
        result = ServicePlugin(
            service=self.service,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=self.ventures,
            forecast=False,
        )
        self.assertEquals(result, {
            3: {
                'sut_3_count': 220.0,
                'sut_3_cost': D('1510'),
                'sut_4_count': 440.0,
                'sut_4_cost': D('2730'),
                '1_service_cost': D('4240'),
            },
            4: {
                'sut_3_count': 440.0,
                'sut_3_cost': D('3020'),
                'sut_4_count': 880.0,
                'sut_4_cost': D('5460'),
                '1_service_cost': D('8480'),
            },
        })

    def test_schema(self):
        result = ServicePlugin(
            service=self.service,
            type='schema'
        )
        self.assertEquals(result, OrderedDict([
            ('sut_3_count', {'name': _('ServiceUsageType1 count')}),
            ('sut_3_cost', {
                'name': _('ServiceUsageType1 cost'),
                'currency': True,
                'total_cost': False,
            }),
            ('sut_4_count', {'name': _('ServiceUsageType2 count')}),
            ('sut_4_cost', {
                'name': _('ServiceUsageType2 cost'),
                'currency': True,
                'total_cost': False,
            }),
            ('1_service_cost', {
                'name': _('Service1 cost'),
                'currency': True,
                'total_cost': True,
            }),
        ]))

    def test_total_cost(self):
        self.assertEqual(
            D(4240),
            ServicePlugin.total_cost(
                datetime.date(2013, 10, 10),
                datetime.date(2013, 10, 20),
                self.service,
                False,
                [self.venture1]
            )
        )

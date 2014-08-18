
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

from ralph_scrooge import models
from ralph_scrooge.plugins.reports.pricing_service import PricingServicePlugin
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    DailyPricingObjectFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    # ServiceFactory,
    TeamFactory,
    UsageTypeFactory,
    WarehouseFactory,
)


class TestPricingServicePlugin(TestCase):
    def setUp(self):
        # usage types
        self.usage_type = UsageTypeFactory(
            by_warehouse=False,
            by_cost=False,
            type='BU',
        )
        self.usage_type_cost_wh = UsageTypeFactory(
            by_warehouse=True,
            by_cost=True,
            type='BU',
        )

        self.pricing_service_usage_type1 = UsageTypeFactory(
            type='SU',
            divide_by=5,
            rounding=2,
        )
        self.pricing_service_usage_type2 = UsageTypeFactory(
            type='SU',
        )

        # warehouses
        self.default_warehouse = models.Warehouse.objects.get(name='Default')
        self.warehouse1 = WarehouseFactory(show_in_report=True)
        self.warehouse2 = WarehouseFactory(show_in_report=True)
        self.warehouses = models.Warehouse.objects.exclude(
            pk=self.default_warehouse.pk
        )

        # pricing service
        self.pricing_service = PricingServiceFactory()

        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 15),
            percent=30,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 15),
            percent=70,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 16),
            end=datetime.date(2013, 10, 30),
            percent=40,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 16),
            end=datetime.date(2013, 10, 30),
            percent=60,
        ).save()
        self.pricing_service.save()

        # service_environments
        self.service_environment1 = ServiceEnvironmentFactory(
            service__pricing_service=self.pricing_service
        )
        self.service_environment2 = ServiceEnvironmentFactory(
            service__pricing_service=self.pricing_service
        )
        self.service_environment3 = ServiceEnvironmentFactory()
        self.service_environment4 = ServiceEnvironmentFactory()

        self.not_service_environments = [
            self.service_environment3,
            self.service_environment4,
        ]
        self.service_environments = models.ServiceEnvironment.objects.all()

        # daily usages of base type
        # ut1:
        #   service_environment1: 10
        #   service_environment2: 20
        # ut2:
        #   service_environment1: 20 (half in warehouse1, half in warehouse2)
        #   service_environment2: 40 (half in warehouse1, half in warehouse2)
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        base_usage_types = models.UsageType.objects.filter(type='BU')
        for k, service_environment in enumerate(
            self.service_environments,
            start=1
        ):
            daily_pricing_object = DailyPricingObjectFactory()
            for i, ut in enumerate(base_usage_types, start=1):
                days = rrule.rrule(rrule.DAILY, dtstart=start, until=end)
                for j, day in enumerate(days, start=1):
                    daily_usage = DailyUsageFactory(
                        date=day,
                        service_environment=service_environment,
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
                daily_pricing_object = DailyPricingObjectFactory(date=day)
                for k, service_environment in enumerate(
                    self.not_service_environments,
                    start=1
                ):
                    daily_usage = models.DailyUsage(
                        date=day,
                        service_environment=service_environment,
                        daily_pricing_object=daily_pricing_object,
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
        result = PricingServicePlugin._get_usage_type_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            forecast=True,
            service_environments=self.service_environments,
        )
        self.assertEquals(result, 100)
        plugin_run_mock.assert_called_with(
            'scrooge_reports',
            self.usage_type.get_plugin_name(),
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            usage_type=self.usage_type,
            forecast=True,
            service_environments=self.service_environments,
            type='total_cost',
        )

    @mock.patch('ralph.util.plugin.run')
    def test_get_usage_type_cost_with_exception(self, plugin_run_mock):
        for exc in (KeyError(), AttributeError()):
            plugin_run_mock.side_effect = exc
            result = PricingServicePlugin._get_usage_type_cost(
                start=datetime.date(2013, 10, 10),
                end=datetime.date(2013, 10, 20),
                usage_type=self.usage_type,
                forecast=True,
                service_environments=self.service_environments,
            )
            self.assertEquals(result, 0)

    # =========================================================================
    # _get_service_base_usage_types_cost
    # =========================================================================
    def test_get_service_base_usage_types_cost(self):
        result = PricingServicePlugin._get_service_base_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
            forecast=False,
            service_environments=self.pricing_service.service_environments,
        )
        # aggregate from test_get_usage_type_cost_by_cost and
        # test_get_usage_type_cost
        self.assertEquals(result, D('12720'))

    def test_get_service_base_usage_types_cost_forecast(self):
        result = PricingServicePlugin._get_service_base_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
            forecast=True,
            service_environments=[self.service_environment1],
        )
        # aggregate from test_get_usage_type_cost_by_cost_forecast and
        # test_get_usage_type_cost_forecast
        self.assertEquals(result, D('8580'))

    def test_get_service_base_usage_types_cost_with_excluded(self):
        self.pricing_service.excluded_base_usage_types.add(
            self.usage_type_cost_wh
        )
        self.pricing_service.save()
        result = PricingServicePlugin._get_service_base_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
            forecast=False,
            service_environments=self.pricing_service.service_environments,
        )
        self.assertEquals(result, D('6600'))

    # =========================================================================
    # _get_service_regular_usage_types_cost
    # =========================================================================
    @mock.patch('ralph.util.plugin.run')
    def test_get_service_regular_usage_types_cost(self, plugin_run_mock):
        regular_usage_type = UsageTypeFactory(type='RU')
        self.pricing_service.regular_usage_types.add(regular_usage_type)
        self.pricing_service.save()

        plugin_run_mock.return_value = D('1000')
        service_environments = self.pricing_service.service_environments
        result = PricingServicePlugin._get_service_regular_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
            forecast=True,
            service_environments=service_environments,
        )
        self.assertEquals(result, D('1000'))
        plugin_run_mock.assert_called_once_with(
            'scrooge_reports',
            regular_usage_type.get_plugin_name(),
            type='total_cost',
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            forecast=True,
            service_environments=service_environments,
            usage_type=regular_usage_type,
        )

    def test_get_service_regular_usage_types_cost_empty(self):
        UsageTypeFactory(type='RU')
        result = PricingServicePlugin._get_service_regular_usage_types_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
            forecast=True,
            service_environments=self.pricing_service.service_environments,
        )
        self.assertEquals(result, D('0'))

    # =========================================================================
    # _get_service_teams_cost
    # =========================================================================
    @mock.patch('ralph.util.plugin.run')
    def test_get_service_teams_cost(self, plugin_run_mock):
        team = TeamFactory()
        plugin_run_mock.return_value = D('1000')
        service_environments = self.pricing_service.service_environments
        result = PricingServicePlugin._get_service_teams_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
            forecast=True,
            service_environments=service_environments,
        )
        self.assertEquals(result, D('1000'))
        plugin_run_mock.assert_called_once_with(
            'scrooge_reports',
            'team',
            type='total_cost',
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            forecast=True,
            service_environments=service_environments,
            team=team,
        )

    # =========================================================================
    # _get_dependent_services_cost
    # =========================================================================

    @mock.patch('ralph_scrooge.models.service.PricingService.get_dependent_services')  # noqa
    @mock.patch('ralph.util.plugin.run')
    def test_get_dependent_services_cost(
        self,
        plugin_run_mock,
        get_dependent_services_mock,
    ):
        dependent_service1 = PricingServiceFactory()
        dependent_service2 = PricingServiceFactory()
        get_dependent_services_mock.return_value = [
            dependent_service1,
            dependent_service2,
        ]

        def pl(chain, func_name, type, pricing_service, **kwargs):
            data = {
                dependent_service1: 100,
                dependent_service2: 200,
            }
            return data[pricing_service]

        plugin_run_mock.side_effect = pl

        start = datetime.date(2013, 10, 10)
        end = datetime.date(2013, 10, 20)
        forecast = True
        service_environments = self.pricing_service.service_environments
        result = PricingServicePlugin._get_dependent_services_cost(
            start=start,
            end=end,
            pricing_service=self.pricing_service,
            forecast=forecast,
            service_environments=service_environments,
        )
        self.assertEquals(result, 300)
        plugin_run_mock.assert_any_call(
            'scrooge_reports',
            'pricing_service_plugin',
            pricing_service=dependent_service1,
            service_environments=service_environments,
            start=start,
            end=end,
            forecast=forecast,
            type='total_cost',
        )
        plugin_run_mock.assert_any_call(
            'scrooge_reports',
            'pricing_service_plugin',
            pricing_service=dependent_service2,
            service_environments=service_environments,
            start=start,
            end=end,
            forecast=forecast,
            type='total_cost',
        )

    # =========================================================================
    # _get_service_extra_cost
    # =========================================================================
    @mock.patch('ralph.util.plugin.run')
    def test_get_service_extra_cost(self, plugin_run_mock):
        plugin_run_mock.side_effect = [122]
        self.assertEqual(
            122,
            PricingServicePlugin._get_service_extra_cost(
                datetime.date(2013, 10, 10),
                datetime.date(2013, 10, 20),
                [self.service_environment1]
            )
        )
        plugin_run_mock.side_effect = KeyError()
        self.assertEqual(
            D(0),
            PricingServicePlugin._get_service_extra_cost(
                datetime.date(2013, 10, 10),
                datetime.date(2013, 10, 20),
                [self.service_environment1]
            )
        )

    # =========================================================================
    # _get_date_ranges_percentage
    # =========================================================================
    def test_get_date_ranges_percentage(self):
        result = PricingServicePlugin._get_date_ranges_percentage(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            pricing_service=self.pricing_service,
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
        self.pricing_service = PricingServiceFactory()
        self.pricing_service_usage_type3 = UsageTypeFactory(type='SU')

        # |__________||____|
        # |____||____||____|
        # |____||__________|
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 20),
            percent=50,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 10),
            percent=30,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type3,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 10),
            percent=20,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 11),
            end=datetime.date(2013, 10, 20),
            percent=10,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type3,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 11),
            end=datetime.date(2013, 10, 30),
            percent=40,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 21),
            end=datetime.date(2013, 10, 30),
            percent=30,
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type2,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 21),
            end=datetime.date(2013, 10, 30),
            percent=30,
        ).save()
        self.pricing_service.save()

        result = PricingServicePlugin._get_date_ranges_percentage(
            start=datetime.date(2013, 10, 5),
            end=datetime.date(2013, 10, 25),
            pricing_service=self.pricing_service,
        )

        self.assertEquals(result, {
            (datetime.date(2013, 10, 5), datetime.date(2013, 10, 10)): {
                self.pricing_service_usage_type1.id: 50.0,
                self.pricing_service_usage_type2.id: 30.0,
                self.pricing_service_usage_type3.id: 20.0,
            },
            (datetime.date(2013, 10, 11), datetime.date(2013, 10, 20)): {
                self.pricing_service_usage_type1.id: 50.0,
                self.pricing_service_usage_type2.id: 10.0,
                self.pricing_service_usage_type3.id: 40.0,
            },
            (datetime.date(2013, 10, 21), datetime.date(2013, 10, 25)): {
                self.pricing_service_usage_type1.id: 30.0,
                self.pricing_service_usage_type2.id: 30.0,
                self.pricing_service_usage_type3.id: 40.0,
            },
        })

    # =========================================================================
    # total_cost
    # =========================================================================
    def test_total_cost(self):
        # add regular usage type
        regular_usage_type = UsageTypeFactory(by_cost=True, type='RU')
        models.DailyUsage(
            type=regular_usage_type,
            service_environment=self.service_environment1,
            daily_pricing_object=DailyPricingObjectFactory(),
            value=100,
            date=datetime.date(2013, 10, 11)
        ).save()
        models.DailyUsage(
            type=regular_usage_type,
            service_environment=self.service_environment2,
            daily_pricing_object=DailyPricingObjectFactory(),
            value=300,
            date=datetime.date(2013, 10, 12)
        ).save()
        models.ServiceUsageTypes(
            usage_type=self.pricing_service_usage_type1,
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 30),
            percent=100,
        ).save()
        models.UsagePrice(
            type=regular_usage_type,
            start=datetime.date(2013, 10, 1),
            end=datetime.date(2013, 10, 30),
            cost=1000
        ).save()
        self.pricing_service.regular_usage_types.add(regular_usage_type)
        self.pricing_service.save()

        self.assertEqual(
            D(4490),
            PricingServicePlugin.total_cost(
                datetime.date(2013, 10, 10),
                datetime.date(2013, 10, 20),
                self.pricing_service,
                False,
                [self.service_environment1]
            )
        )

    # =========================================================================
    # schema
    # =========================================================================
    def test_schema(self):
        result = PricingServicePlugin(
            pricing_service=self.pricing_service,
            type='schema'
        )
        self.assertEquals(result, OrderedDict([
            (
                'service_{}_sut_{}_count'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type1.id
                ),
                {
                    'name': _('{} count'.format(
                        self.pricing_service_usage_type1.name
                    )),
                    'divide_by': 5,
                    'rounding': 2,
                }
            ),
            (
                'service_{}_sut_{}_cost'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type1.id
                ),
                {
                    'name': _('{} cost'.format(
                        self.pricing_service_usage_type1.name
                    )),
                    'currency': True,
                    'total_cost': False,
                }
            ),
            (
                'service_{}_sut_{}_count'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type2.id
                ),
                {
                    'name': _('{} count'.format(
                        self.pricing_service_usage_type2.name
                    )),
                    'divide_by': 0,
                    'rounding': 0,
                }
            ),
            (
                'service_{}_sut_{}_cost'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type2.id
                ),
                {
                    'name': _('{} cost'.format(
                        self.pricing_service_usage_type2.name
                    )),
                    'currency': True,
                    'total_cost': False,
                }
            ),
            ('{}_service_cost'.format(self.pricing_service.id), {
                'name': _('{} cost'.format(self.pricing_service.name)),
                'currency': True,
                'total_cost': True,
            }),
        ]))

    # =========================================================================
    # costs (and plugin usage)
    # =========================================================================
    def test_plugin_call(self):
        result = PricingServicePlugin(
            pricing_service=self.pricing_service,
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            service_environments=self.service_environments,
            forecast=False,
        )
        self.assertEquals(result, {
            self.service_environment3.id: {
                'service_{}_sut_{}_count'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type1.id
                ): 220.0,
                'service_{}_sut_{}_cost'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type1.id
                ): D('1510'),
                'service_{}_sut_{}_count'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type2.id
                ): 440.0,
                'service_{}_sut_{}_cost'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type2.id
                ): D('2730'),
                '{}_service_cost'.format(self.pricing_service.id): D('4240'),
            },
            self.service_environment4.id: {
                'service_{}_sut_{}_count'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type1.id
                ): 440.0,
                'service_{}_sut_{}_cost'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type1.id
                ): D('3020'),
                'service_{}_sut_{}_count'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type2.id
                ): 880.0,
                'service_{}_sut_{}_cost'.format(
                    self.pricing_service.id,
                    self.pricing_service_usage_type2.id
                ): D('5460'),
                '{}_service_cost'.format(self.pricing_service.id): D('8480'),
            },
        })

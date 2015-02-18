# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
from datetime import date
from dateutil import rrule

from django.test import TestCase

from ralph_scrooge.management.commands.scrooge_tenants_instances import (
    Command
)
from ralph_scrooge.models import DailyCost, PRICING_OBJECT_TYPES
from ralph_scrooge.tests.utils.factory import (
    DailyCostFactory,
    DailyUsageFactory,
    TenantInfoFactory,
    UsagePriceFactory,
    UsageTypeFactory,
)
from ralph_scrooge.utils.common import AttributeDict


class TestScroogeTenantsInstances(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.start = date(2014, 11, 12)
        self.end = date(2014, 11, 15)
        self.yesterday = date(2014, 11, 11)

        self.tenants = TenantInfoFactory.create_batch(
            3,
            type_id=PRICING_OBJECT_TYPES.TENANT,
            model__type_id=PRICING_OBJECT_TYPES.TENANT
        )

        # usage types
        self.ceilometer_usage1 = UsageTypeFactory(name='openstack.flavor1')
        self.ceilometer_usage2 = UsageTypeFactory(name='openstack.flavor2')
        self.simple_usage1 = UsageTypeFactory(name='OpenStack Usage 1')
        self.simple_usage2 = UsageTypeFactory(name='OpenStack Usage 2')

        for day in rrule.rrule(
            rrule.DAILY,
            dtstart=self.yesterday,
            until=self.end
        ):
            for tenant in self.tenants:
                dpo = tenant.get_daily_pricing_object(day)
                for usage_type, val in [
                    (self.ceilometer_usage1, 24),
                    (self.ceilometer_usage2, 48),
                    (self.simple_usage1, 24),
                    (self.simple_usage2, 48),
                ]:
                    DailyUsageFactory(
                        daily_pricing_object=dpo,
                        date=day,
                        type=usage_type,
                        value=val,
                        service_environment=tenant.service_environment,
                    )
                    for forecast in [True, False]:
                        value = val * (2 if forecast else 1)
                        DailyCostFactory(
                            pricing_object=tenant,
                            date=day,
                            value=value,
                            cost=value,
                            forecast=forecast,
                            type=usage_type,
                            service_environment=tenant.service_environment,
                        )

        self.command = Command()

    def test_headers_ceilometer(self):
        self.command.type = 'ceilometer'
        result = self.command.HEADERS
        self.assertEqual(result, [
            'Service',
            'Environment',
            'Model',
            'OpenStack Tenant ID',
            'OpenStack Tenant',
            'Flavor',
            'Total usage',
            'Instances (avg)',
            'Hour price',
            'Cost',
        ])

    def test_headers_simple_usage(self):
        self.command.type = 'simple_usage'
        result = self.command.HEADERS
        self.assertEqual(result, [
            'Service',
            'Environment',
            'Model',
            'OpenStack Tenant ID',
            'OpenStack Tenant',
            'Resource',
            'Total usage',
            'Avg usage per day',
            'Unit price',
            'Cost',
        ])

    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.Collector._get_dates')  # noqa
    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.Collector.get_plugins')  # noqa
    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.Collector.process')  # noqa
    def test_calculate_missing_dates(
        self,
        process_mock,
        get_plugins_mock,
        get_dates_mock
    ):
        plugins_names = set(['pl1', 'pl2', 'pl3'])
        plugins = map(lambda x: AttributeDict(name=x), plugins_names)
        dates = [date(2014, 11, 10), date(2014, 11, 12)]
        get_plugins_mock.return_value = plugins[:2]
        get_dates_mock.return_value = dates
        self.command._calculate_missing_dates(
            self.start,
            self.end,
            True,
            plugins_names
        )
        calls = []
        for day in dates:
            calls.append(mock.call(
                day,
                True,
                plugins[:2],
            ))
        process_mock.assert_has_calls(calls)

    def _set_usage_prices(self):
        self.usage_price1 = UsagePriceFactory(
            type=self.ceilometer_usage1,
            start=date(2014, 11, 1),
            end=date(2014, 11, 13),
            price=10,
            forecast_price=20,
        )
        self.usage_price2 = UsagePriceFactory(
            type=self.ceilometer_usage1,
            start=date(2014, 11, 14),
            end=date(2014, 11, 30),
            price=30,
            forecast_price=40,
        )
        UsagePriceFactory(
            type=self.ceilometer_usage2,
            start=date(2014, 11, 1),
            end=date(2014, 11, 30),
            price=10,
            forecast_price=20,
        )
        UsagePriceFactory(
            type=self.simple_usage1,
            start=date(2014, 11, 1),
            end=date(2014, 11, 30),
            price=10,
            forecast_price=20,
        )
        UsagePriceFactory(
            type=self.simple_usage2,
            start=date(2014, 11, 1),
            end=date(2014, 11, 30),
            price=30,
            forecast_price=40,
        )

    def test_get_usage_prices(self):
        self._set_usage_prices()
        result = self.command._get_usage_prices(
            self.ceilometer_usage1.id,
            self.start,
            self.end,
            False,
        )
        self.assertEqual(result, (self.ceilometer_usage1, '10 / 30'))

    def test_get_usage_prices_forecast(self):
        self._set_usage_prices()
        result = self.command._get_usage_prices(
            self.ceilometer_usage1.id,
            self.start,
            self.end,
            True,
        )
        self.assertEqual(result, (self.ceilometer_usage1, '20 / 40'))

    def test_parse_date(self):
        d = '2014-11-12'
        result = self.command._parse_date(d)
        self.assertEqual(result, date(2014, 11, 12))

    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.date')  # noqa
    def test_parse_date_yesterday(self, mock_date):
        mock_date.today.return_value = date(2014, 11, 13)
        result = self.command._parse_date(None)
        self.assertEqual(result, date(2014, 11, 12))

    def test_get_costs_ceilometer(self):
        self._set_usage_prices()
        result = self.command.get_costs(
            self.start,
            self.end,
            False,
            {'type__name__startswith': 'openstack.'}
        )
        expected = []
        days = (self.end - self.start).days + 1
        for tenant in self.tenants:
            for usage_type, value, prices in [
                (self.ceilometer_usage1, 1, '10 / 30'),
                (self.ceilometer_usage2, 2, '10'),
            ]:
                expected.append([
                    tenant.service_environment.service.name,
                    tenant.service_environment.environment.name,
                    tenant.model.name,
                    tenant.id,
                    tenant.name,
                    usage_type.name,
                    value * days * 24,
                    value,
                    prices,
                    value * days * 24,
                ])
        self.assertItemsEqual(result, expected)

    def test_get_costs_simple_usage(self):
        self.command.type = 'simple_usage'
        self._set_usage_prices()
        result = self.command.get_costs(
            self.start,
            self.end,
            False,
            {'type__name__startswith': 'OpenStack '}
        )
        expected = []
        days = (self.end - self.start).days + 1
        for tenant in self.tenants:
            for usage_type, value, prices in [
                (self.simple_usage1, 1, '10'),
                (self.simple_usage2, 2, '30'),
            ]:
                expected.append([
                    tenant.service_environment.service.name,
                    tenant.service_environment.environment.name,
                    tenant.model.name,
                    tenant.id,
                    tenant.name,
                    usage_type.name,
                    value * days * 24,
                    value * 24,
                    prices,
                    value * days * 24,
                ])
        self.assertItemsEqual(result, expected)

    def test_get_costs_ceilometer_forecast(self):
        self._set_usage_prices()
        result = self.command.get_costs(
            self.start,
            self.end,
            True,
            {'type__name__startswith': 'openstack.'}
        )
        expected = []
        days = (self.end - self.start).days + 1
        for tenant in self.tenants:
            for usage_type, value, prices in [
                (self.ceilometer_usage1, 2, '20 / 40'),
                (self.ceilometer_usage2, 4, '20'),
            ]:
                expected.append([
                    tenant.service_environment.service.name,
                    tenant.service_environment.environment.name,
                    tenant.model.name,
                    tenant.id,
                    tenant.name,
                    usage_type.name,
                    value * days * 24,
                    value,
                    prices,
                    value * days * 24,
                ])
        self.assertItemsEqual(result, expected)

    def test_get_usages_without_cost_ceilometer(self):
        DailyCost.objects.filter(type=self.ceilometer_usage1).delete()
        result = self.command.get_usages_without_cost(
            self.start,
            self.end,
            False,
            {'type__name__startswith': 'openstack.'}
        )
        usage_type = self.ceilometer_usage1
        value = 1
        expected = []
        days = (self.end - self.start).days + 1
        for tenant in self.tenants:
            expected.append([
                tenant.service_environment.service.name,
                tenant.service_environment.environment.name,
                tenant.model.name,
                tenant.id,
                tenant.name,
                usage_type.name,
                value * days * 24,
                value,
                '-',
                '-',
            ])
        self.assertItemsEqual(result, expected)

    def test_get_usages_without_cost_simple_usage(self):
        self.command.type = 'simple_usage'
        DailyCost.objects.filter(type=self.simple_usage1).delete()
        result = self.command.get_usages_without_cost(
            self.start,
            self.end,
            False,
            {'type__name__startswith': 'OpenStack'}
        )
        usage_type = self.simple_usage1
        value = 1
        days = (self.end - self.start).days + 1
        expected = []
        for tenant in self.tenants:
            expected.append([
                tenant.service_environment.service.name,
                tenant.service_environment.environment.name,
                tenant.model.name,
                tenant.id,
                tenant.name,
                usage_type.name,
                value * days * 24,
                value * 24,
                '-',
                '-',
            ])
        self.assertItemsEqual(result, expected)

    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.Command._calculate_missing_dates')  # noqa
    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.Command.get_costs')  # noqa
    @mock.patch('ralph_scrooge.management.commands.scrooge_tenants_instances.Command.get_usages_without_cost')  # noqa
    def _test_get_data(self, type, filters, usages_mock, cost_mock, calc_mock):
        usages = [
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
        ]
        costs = [
            ['1', '2', '3'],
            ['4', '5', '6'],
        ]
        usages_mock.return_value = usages
        cost_mock.return_value = costs
        calc_mock.return_value = None
        self.command.type = type
        result = self.command.get_data(
            self.start.isoformat(),
            self.end.isoformat(),
            True,
            ['plugin1']
        )
        self.assertEqual(result, costs + usages)
        cost_mock.assert_called_once_with(self.start, self.end, True, filters)
        usages_mock.assert_called_once_with(
            self.start,
            self.end,
            True,
            filters
        )
        calc_mock.assert_called_once_with(
            self.start,
            self.end,
            True,
            ['plugin1']
        )

    def test_get_data_ceilometer(self):
        self._test_get_data(
            'ceilometer',
            {'type__name__startswith': 'openstack.'}
        )

    def test_get_data_simple_usage(self):
        self._test_get_data(
            'simple_usage',
            {'type__name__startswith': 'OpenStack '}
        )

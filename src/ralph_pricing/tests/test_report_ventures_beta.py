# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
from collections import OrderedDict
from decimal import Decimal as D

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.views.ventures_beta import AllVenturesBeta as AllVentures


class TestReportVenturesBeta(TestCase):
    def setUp(self):
        self.day = day = datetime.date(2013, 4, 25)

        # ventures
        self.venture = models.Venture(venture_id=1, name='b', is_active=True)
        self.venture.save()
        self.subventure = models.Venture(
            venture_id=2,
            parent=self.venture,
            name='bb',
            is_active=False,
        )
        self.subventure.save()
        self.venture2 = models.Venture(venture_id=3, name='a', is_active=True)
        self.venture2.save()

        # devices (assets)
        device = models.Device(
            device_id=3,
            asset_id=5,
        )
        device.save()
        daily = models.DailyDevice(
            pricing_device=device,
            date=day,
            name='ziew',
            price=1337,
            pricing_venture=self.venture,
        )
        daily.save()

        other_device = models.Device(
            device_id=2,
            asset_id=3,
        )
        other_device.save()
        other_daily = models.DailyDevice(
            pricing_device=other_device,
            date=day,
            name='ziew',
            price=833833,
            pricing_venture=self.subventure,
        )
        other_daily.save()

        # warehouse
        self.warehouse = models.Warehouse(name='Warehouse1')
        self.warehouse.save()

        # usages
        usage_type = models.UsageType(name='UT1', symbol='ut1')
        usage_type.save()
        daily_usage = models.DailyUsage(
            type=usage_type,
            value=32,
            date=day,
            pricing_venture=self.venture,
        )
        daily_usage.save()
        usage_type3 = models.UsageType(
            name='UT2',
            symbol='ut2',
            show_in_report=False,
        )
        usage_type3.save()

        # usages by warehouse
        warehouse_usage_type = models.UsageType(
            name='UT3',
            symbol='ut3',
            by_warehouse=True,
            order=3,
        )
        warehouse_usage_type.save()
        daily_warehouse_usage = models.DailyUsage(
            type=warehouse_usage_type,
            value=120,
            date=day,
            pricing_venture=self.venture,
            warehouse=self.warehouse,
        )
        daily_warehouse_usage.save()

    def test_get_plugins(self):
        """
        Test plugins list based on visible usage types
        """
        plugins = AllVentures._get_plugins()
        self.assertEquals(plugins, [
            dict(name='Information', symbol='information'),
            dict(name='Deprecation', symbol='deprecation'),
            dict(name='UT3', symbol='ut3'),  # order matters
            dict(name='UT1', symbol='ut1'),
        ])

    def test_get_as_currency(self):
        """
        Test if decimal is properly 'transformed' to currency
        """
        currency = AllVentures._get_as_currency('1234', False)
        self.assertEquals(currency, ('1234.00 PLN', D(0)))

    def test_get_as_currency_total_cost(self):
        """
        Test if total cost decimal is properly 'transformed' to currency
        """
        currency = AllVentures._get_as_currency(1234, True)
        self.assertEquals(currency, ('1234.00 PLN', D('1234')))

    def test_prepare_field_value_in_venture_data(self):
        """
        Test if field is properly prepared for placing it in report. Value
        in venture data.
        """
        venture_data = {
            'field1': '1234',
        }
        rules = {
            'currency': False
        }
        result = AllVentures._prepare_field('field1', rules, venture_data)
        self.assertEquals(result, ('1234', D(0)))

    def test_prepare_field_value_in_venture_data_currency(self):
        """
        Test if field is properly prepared for placing it in report. Value
        in venture data.
        """
        venture_data = {
            'field1': 1234,
        }
        rules = {
            'currency': True,
            'total_cost': True,
        }
        result = AllVentures._prepare_field('field1', rules, venture_data)
        self.assertEquals(result, ('1234.00 PLN', D('1234')))

    def test_prepare_field_value_not_in_venture_date_default(self):
        """
        Test if field is properly prepared for placing it in report. Value not
        in venture data and there is no default rule.
        """
        venture_data = {}
        rules = {
            'currency': True,
            'total_cost': True,
            'default': 3,
        }
        result = AllVentures._prepare_field('field1', rules, venture_data)
        self.assertEquals(result, ('3.00 PLN', D('3')))

    def test_prepare_field_value_not_in_venture_date(self):
        """
        Test if field is properly prepared for placing it in report. Value not
        in venture data and there is default rule.
        """
        venture_data = {}
        rules = {
            'currency': True,
            'total_cost': True,
        }
        result = AllVentures._prepare_field('field1', rules, venture_data)
        self.assertEquals(result, ('0.00 PLN', D('0')))

    def test_prepare_field_value_basestring(self):
        """
        Test if field is properly prepared for placing it in report. Value is
        string.
        """
        venture_data = {
            'field1': '123'
        }
        rules = {
            'currency': True,
            'total_cost': True,
        }
        result = AllVentures._prepare_field('field1', rules, venture_data)
        self.assertEquals(result, ('123', D('0')))

    def _sample_schema(self):
        return [
            OrderedDict([
                ('field1', {'name': 'Field1'}),
                ('field2', {'name': 'Field2', 'currency': True}),
            ]),
            OrderedDict([
                ('field3', {'name': 'Field3'}),
                ('field4', {'name': 'Field4'}),
            ]),
        ]

    @mock.patch.object(AllVentures, '_get_schema')
    def test_prepare_row(self, get_schema_mock):
        """
        Test if whole row is properly prepared for placing it in report
        """
        venture_data = {
            'field1': 123,
            'field2': 34,
            'field3': 3123,
            'field4': 3434
        }
        get_schema_mock.return_value = self._sample_schema()
        result = AllVentures._prepare_venture_row(venture_data)
        self.assertEquals(result, [123, u'34.00 PLN', 3123, 3434, u'0.00 PLN'])

    def test_get_ventures(self):
        """
        Test if ventures are correctly filtered
        """
        def get_id(l):
            return [i.id for i in l]

        ventures1 = AllVentures._get_ventures(is_active=True)
        self.assertEquals(get_id(ventures1),
                          get_id([self.venture2, self.venture]))

        ventures1 = AllVentures._get_ventures(is_active=False)
        self.assertEquals(
            get_id(ventures1),
            get_id([self.venture2, self.venture, self.subventure])
        )

    def test_get_report_data(self):
        """
        Test generating data for whole report
        """
        raise NotImplementedError()

    @mock.patch.object(AllVentures, '_get_schema')
    def test_get_header(self, get_schema_mock):
        """
        Test getting headers for report
        """
        get_schema_mock.return_value = self._sample_schema()
        result = AllVentures.get_header()
        self.assertEquals(
            result,
            ['Field1', 'Field2', 'Field3', 'Field4', 'Total cost']
        )

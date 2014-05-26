# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
from collections import OrderedDict
from decimal import Decimal as D
from dateutil import rrule

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ralph_pricing import models
from ralph_pricing.tests import utils
from ralph_pricing.views.devices import Devices


class TestReportDevices(TestCase):
    def setUp(self):
        self.report_start = datetime.date(2013, 4, 20)
        self.report_end = datetime.date(2013, 4, 30)
        # ventures
        self.venture = utils.get_or_create_venture()
        self.subventure = utils.get_or_create_venture(parent=self.venture)

        # usages
        self.usage_type = models.UsageType(
            name='UT1',
            symbol='ut1',
            type='BU',
            show_in_devices_report=True,
        )
        self.usage_type.save()
        usage_type2 = models.UsageType(
            name='UT2',
            symbol='ut2',
            type='BU',
            show_in_devices_report=False,
        )
        usage_type2.save()

        # usages by warehouse
        self.warehouse_usage_type = models.UsageType(
            name='UT3',
            symbol='ut3',
            by_warehouse=True,
            order=3,
            type='BU',
            use_universal_plugin=False,
            show_in_devices_report=True,
        )
        self.warehouse_usage_type.save()

        # devices
        self.device1 = utils.get_or_create_device()
        self.device2 = utils.get_or_create_device()
        self.device3 = utils.get_or_create_device()  # device without daily
        self.device_virtual = utils.get_or_create_device(is_virtual=True)

        # dailydevices
        days = rrule.rrule(
            rrule.DAILY,
            dtstart=self.report_start,
            until=self.report_end,
        )
        for device in (self.device1, self.device2, self.device_virtual):
            for j, day in enumerate(days, start=1):
                dailydevice = utils.get_or_create_dailydevice(
                    date=day,
                    device=device,
                    venture=self.venture
                )
                dailydevice.save()

    def test_get_plugins(self):
        """
        Test plugins list based on visible usage types
        """
        plugins = Devices.get_plugins()
        self.assertEquals(plugins, [
            dict(name='Information', plugin_name='information'),
            dict(
                name='UT3',
                plugin_name=self.warehouse_usage_type.get_plugin_name(),
                plugin_kwargs=dict(
                    usage_type=self.warehouse_usage_type,
                    no_price_msg=True,
                ),
            ),  # order matters
            dict(
                name='UT1',
                plugin_name=self.usage_type.get_plugin_name(),
                plugin_kwargs=dict(
                    usage_type=self.usage_type,
                    no_price_msg=True,
                ),
            ),
        ])

    def test_get_devices(self):
        """
        Test if field is properly prepared for placing it in report. Value
        in venture data.
        """
        devices = Devices._get_devices(
            self.report_start,
            self.report_end,
            [self.venture]
        )
        self.assertEquals(list(devices), [self.device1, self.device2])

    def test_get_ventures(self):
        ventures = Devices._get_ventures(self.venture, use_subventures=False)
        self.assertEquals(ventures, [self.venture])

    def test_get_ventures_with_subventures(self):
        ventures = Devices._get_ventures(self.venture, use_subventures=True)
        self.assertEquals(ventures, [self.venture, self.subventure])

    def _sample_schema(self):
        return [
            OrderedDict([
                ('field1', {'name': 'Field1'}),
                ('field2', {
                    'name': 'Field2',
                    'currency': True,
                    'total_cost': True,
                }),
            ]),
            OrderedDict([
                ('field3', {'name': 'Field3'}),
                ('field4', {
                    'name': 'Field4',
                    'currency': True,
                    'total_cost': True,
                }),
            ]),
        ]

    @mock.patch('ralph.util.plugin.run')
    def test_get_report_data(self, plugin_run_mock):
        """
        Test generating data for whole report
        """
        def pl(chain, func_name, type, **kwargs):
            """
            Mock for plugin run. Should replace every schema and report plugin
            """
            data = {
                'information': {
                    'schema_devices': OrderedDict([
                        ('barcode', {'name': 'Barcode'}),
                        ('sn', {'name': 'SN'}),
                        ('name', {'name': 'Device name'}),
                    ]),
                    'costs_per_device': {
                        self.device1.id: {
                            'sn': '1111-1111-1111',
                            'barcode': '12345',
                            'name': 'device1',
                        },
                        self.device2.id: {
                            'sn': '1111-1111-1112',
                            'barcode': '12346',
                            'name': 'device2',
                        }
                    },
                },
                'usage_plugin': {
                    'schema_devices': OrderedDict([
                        ('ut1_count', {'name': 'UT1 count'}),
                        ('ut1_cost', {
                            'name': 'UT1 cost',
                            'currency': True,
                            'total_cost': True,
                        })
                    ]),
                    'costs_per_device': {
                        self.device2.id: {
                            'ut1_count': 123,
                            'ut1_cost': D('23.23')
                        },
                    },
                },
                'ut3': {
                    'schema_devices': OrderedDict([
                        ('ut3_count_warehouse_1', {'name': 'UT3 count wh 1'}),
                        ('ut3_count_warehouse_2', {'name': 'UT3 count wh 2'}),
                        ('ut3_cost_warehouse_1', {
                            'name': 'UT3 cost wh 1',
                            'currency': True,
                        }),
                        ('ut3_cost_warehouse_2', {
                            'name': 'UT3 cost wh 2',
                            'currency': True
                        }),
                        ('ut3_cost_total', {
                            'name': 'UT3 total cost',
                            'currency': True,
                            'total_cost': True,
                        })
                    ]),
                    'costs_per_device': {
                        self.device1.id: {
                            'ut3_count_warehouse_1': 267,
                            'ut3_cost_warehouse_1': D('4764.21'),
                            'ut3_count_warehouse_2': 36774,
                            'ut3_cost_warehouse_2': _('Incomplete price'),
                            'ut3_cost_total': D('4764.21'),
                        },
                        self.device2.id: {
                            'ut3_count_warehouse_1': 213,
                            'ut3_cost_warehouse_1': D('434.21'),
                            'ut3_count_warehouse_2': 3234,
                            'ut3_cost_warehouse_2': D('123.21'),
                            'ut3_cost_total': D('557.42'),
                        },
                    }
                },
            }
            if type == 'costs_per_device':
                self.assertTrue(kwargs.get('forecast'))
            result = data.get(func_name, {}).get(type)
            if result is not None:
                return result
            raise KeyError()

        plugin_run_mock.side_effect = pl
        result = None
        for percent, result in Devices.get_data(
            self.report_start,
            self.report_end,
            venture=self.venture,
            forecast=True,
        ):
            pass
        self.assertEquals(result, [
            [
                '12345',  # barcode
                '1111-1111-1111',  # sn
                'device1',  # device name
                267,  # ut3_count_warehouse_1
                36774,  # ut3_cost_warehouse_1
                '4764.21',  # ut3_count_warehouse_2
                'Incomplete price',  # ut3_cost_warehouse_2
                '4764.21',  # ut3_cost_total
                0.0,  # ut1_count
                '0.00',  # ut1_cost
                '4764.21',  # total_cost
            ],
            [
                '12346',  # barcode
                '1111-1111-1112',  # sn
                'device2',  # device name
                213.00,  # ut3_count_warehouse_1
                3234.00,  # ut3_cost_warehouse_1
                '434.21',  # ut3_count_warehouse_2
                '123.21',  # ut3_cost_warehouse_2
                '557.42',  # ut3_cost_total
                123.00,  # ut1_count
                '23.23',  # ut1_cost
                '580.65',  # total_cost
            ]
        ])

    @mock.patch.object(Devices, '_get_schema')
    def test_get_header(self, get_schema_mock):
        """
        Test getting headers for report
        """
        get_schema_mock.return_value = self._sample_schema()
        result = Devices.get_header()
        self.assertEquals(result, [[
            'Field1',
            'Field2 - PLN',
            'Field3',
            'Field4 - PLN',
            'Total cost'
        ]])

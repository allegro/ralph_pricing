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
from django.utils.translation import ugettext_lazy as _

from ralph_pricing import models
from ralph_pricing.tests import utils
from ralph_pricing.views.ventures import AllVentures


class TestReportVentures(TestCase):
    def setUp(self):
        self.report_start = datetime.date(2013, 4, 20)
        self.report_end = datetime.date(2013, 4, 30)
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

        # usages
        self.usage_type = models.UsageType(name='UT1', symbol='ut1')
        self.usage_type.save()
        usage_type2 = models.UsageType(
            name='UT2',
            symbol='ut2',
            show_in_ventures_report=False,
        )
        usage_type2.save()

        # usages by warehouse
        self.warehouse_usage_type = models.UsageType(
            name='UT3',
            symbol='ut3',
            by_warehouse=True,
            order=3,
            use_universal_plugin=False,
        )
        self.warehouse_usage_type.save()

        # service
        self.service = models.Service(
            name='Service1'
        )
        self.service.save()

    def test_get_plugins(self):
        """
        Test plugins list based on visible usage types
        """
        plugins = AllVentures.get_plugins()
        self.maxDiff = None
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
            dict(
                name='Service1',
                plugin_name=self.service.get_plugin_name(),
                plugin_kwargs=dict(
                    service=self.service,
                ),
            ),
            dict(name='ExtraCostsPlugin', plugin_name='extra_cost_plugin'),
        ])

    def test_get_ventures(self):
        """
        Test if ventures are correctly filtered
        """
        get_ids = lambda l: [i.id for i in l]

        ventures1 = AllVentures._get_ventures(is_active=True)
        self.assertEquals(get_ids(ventures1),
                          get_ids([self.venture2, self.venture]))

        ventures1 = AllVentures._get_ventures(is_active=False)
        self.assertEquals(
            get_ids(ventures1),
            get_ids([self.venture2, self.venture, self.subventure])
        )

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
                    'schema': OrderedDict([
                        ('venture_id', {'name': 'ID'}),
                        ('venture', {'name': 'Venture'}),
                        ('department', {'name': 'Department'}),
                    ]),
                    'costs': {
                        1: {
                            'venture_id': 1,
                            'venture': 'b',
                            'department': 'aaaa',
                        },
                        3: {
                            'venture_id': 3,
                            'venture': 'a',
                            'department': 'bbbb',
                        }
                    },
                },
                'usage_plugin': {
                    'schema': OrderedDict([
                        ('ut1_count', {'name': 'UT1 count'}),
                        ('ut1_cost', {
                            'name': 'UT1 cost',
                            'currency': True,
                            'total_cost': True,
                        })
                    ]),
                    'costs': {
                        1: {'ut1_count': 123, 'ut1_cost': D('23.23')},
                    },
                },
                'ut3': {
                    'schema': OrderedDict([
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
                    'costs': {
                        1: {
                            'ut3_count_warehouse_1': 213,
                            'ut3_cost_warehouse_1': D('434.21'),
                            'ut3_count_warehouse_2': 3234,
                            'ut3_cost_warehouse_2': D('123.21'),
                            'ut3_cost_total': D('557.42'),
                        },
                        3: {
                            'ut3_count_warehouse_1': 267,
                            'ut3_cost_warehouse_1': D('4764.21'),
                            'ut3_count_warehouse_2': 36774,
                            'ut3_cost_warehouse_2': _('Incomplete price'),
                            'ut3_cost_total': D('4764.21'),
                        }
                    }
                },
                'service_plugin': {
                    'schema': OrderedDict([
                        ('sut_3_count', {'name': 'UT3 count'}),
                        ('sut_3_cost', {
                            'name': 'UT3 cost wh 1',
                            'currency': True,
                        }),
                        ('sut_4_count', {'name': 'UT4 count'}),

                        ('sut_4_cost', {
                            'name': 'UT4 cost',
                            'currency': True
                        }),
                        ('1_service_cost', {
                            'name': 'Service1 cost',
                            'currency': True,
                            'total_cost': True,
                        })
                    ]),
                    'costs': {
                        1: {
                            'sut_4_count': 40.0,
                            'sut_4_cost': D('2212.11'),
                            '1_service_cost': D('2212.11'),
                        },
                        3: {
                            'sut_3_count': 10.0,
                            'sut_3_cost': D('20.22'),
                            'sut_4_count': 20.0,
                            'sut_4_cost': D('1212.11'),
                            '1_service_cost': D('1232.33'),
                        },
                    }
                }
            }
            result = data.get(func_name, {}).get(type)
            if result is not None:
                return result
            raise KeyError()

        plugin_run_mock.side_effect = pl
        result = None
        for percent, result in AllVentures.get_data(
            self.report_start,
            self.report_end,
            is_active=True,
        ):
            pass
        self.assertEquals(result, [
            [
                3,  # venture_id
                'a',  # venture_name
                'bbbb',  # department
                # 1,  # asset_count
                # '23.00 PLN',  # asset_cost
                267,  # ut3_count_warehouse_1
                36774,  # ut3_cost_warehouse_1
                '4764.21',  # ut3_count_warehouse_2
                'Incomplete price',  # ut3_cost_warehouse_2
                '4764.21',  # ut3_cost_total
                0.0,  # ut1_count
                '0.00',  # ut1_cost
                10.0,  # sut_3_count
                '20.22',  # sut_3_cost,
                20.0,  # sut_4_count
                '1212.11',  # sut_4_count
                '1232.33',  # 1_sercive_cost
                '5996.54',  # total_cost
            ],
            [
                1,  # venture_id
                'b',  # venture_name
                'aaaa',  # department
                # 12,  # asset_count
                # '213.00 PLN',  # asset_cost
                213.00,  # ut3_count_warehouse_1
                3234.00,  # ut3_cost_warehouse_1
                '434.21',  # ut3_count_warehouse_2
                '123.21',  # ut3_cost_warehouse_2
                '557.42',  # ut3_cost_total
                123.00,  # ut1_count
                '23.23',  # ut1_cost
                0.0,  # sut_3_count
                '0.00',  # sut_3_cost,
                40.0,  # sut_4_count
                '2212.11',  # sut_4_count
                '2212.11',  # 1_sercive_cost
                '2792.76',  # total_cost
            ]
        ])

    @mock.patch.object(AllVentures, '_get_schema')
    def test_get_header(self, get_schema_mock):
        """
        Test getting headers for report
        """
        get_schema_mock.return_value = utils.sample_schema()
        result = AllVentures.get_header()
        self.assertEquals(result, [[
            'Field1',
            'Field2 - PLN',
            'Field3',
            'Field4 - PLN',
            'Total cost'
        ]])

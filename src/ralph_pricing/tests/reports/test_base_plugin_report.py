# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock
from decimal import Decimal as D

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.tests import utils
from ralph_pricing.views.base_plugin_report import BasePluginReport


class TestBasePluginReport(TestCase):
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

    def test_prepare_field_value_in_data(self):
        """
        Test if field is properly prepared for placing it in report. Value
        in data.
        """
        data = {
            'field1': '1234',
        }
        rules = {
            'currency': False
        }
        result = BasePluginReport._prepare_field('field1', rules, data)
        self.assertEquals(result, ('1234', D('0')))

    def test_prepare_field_value_in_data_currency(self):
        """
        Test if field is properly prepared for placing it in report. Value
        in data.
        """
        data = {
            'field1': 1234,
        }
        rules = {
            'currency': True,
            'total_cost': True,
        }
        result = BasePluginReport._prepare_field('field1', rules, data)
        self.assertEquals(result, ('1234.00', D('1234')))

    def test_prepare_field_value_not_in_data_default(self):
        """
        Test if field is properly prepared for placing it in report. Value not
        in data and there is no default rule.
        """
        data = {}
        rules = {
            'currency': True,
            'total_cost': True,
            'default': 3,
        }
        result = BasePluginReport._prepare_field('field1', rules, data)
        self.assertEquals(result, ('3.00', D('3')))

    def test_prepare_field_value_not_in_data(self):
        """
        Test if field is properly prepared for placing it in report. Value not
        in data and there is default rule.
        """
        data = {}
        rules = {
            'currency': True,
            'total_cost': True,
        }
        result = BasePluginReport._prepare_field('field1', rules, data)
        self.assertEquals(result, ('0.00', D('0')))

    def test_prepare_field_value_basestring(self):
        """
        Test if field is properly prepared for placing it in report. Value is
        string.
        """
        data = {
            'field1': '123'
        }
        rules = {
            'currency': True,
            'total_cost': True,
        }
        result = BasePluginReport._prepare_field('field1', rules, data)
        self.assertEquals(result, ('123', D('0')))

    @mock.patch.object(BasePluginReport, '_get_schema')
    def test_prepare_row(self, get_schema_mock):
        """
        Test if whole row is properly prepared for placing it in report
        """
        data = {
            'field1': 123,
            'field2': D('3'),
            'field3': 3123,
            'field4': 33
        }
        get_schema_mock.return_value = utils.sample_schema()
        result = BasePluginReport._prepare_row(data)
        self.assertEquals(
            result,
            [123, '3.00', 3123, '33.00', '36.00']
        )

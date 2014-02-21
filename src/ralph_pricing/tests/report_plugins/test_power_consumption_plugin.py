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
from ralph_pricing.plugins.reports.power_consumption import (
    PowerConsumptionSchema,
    PowerConsumptionUsages
)


def pc_get_usages_and_costs(
    start,
    end,
    ventures,
    usage_type,
    warehouse=None,
):
    if warehouse.name == 'Warehouse1':
        return {
            1: {'value': 123, 'cost': D('213.22')},
            2: {'value': 1244, 'cost': D('2323.32')},
            3: {'value': 231, 'cost': 'No price'},
        }
    return {
        1: {'value': 43, 'cost': D('5656.22')},
        2: {'value': 32, 'cost': D('213.32')},
        4: {'value': 123, 'cost': D('123.12')},
    }


class TestPowerConsumptionPlugin(TestCase):
    def setUp(self):
        self.start = datetime.date(2013, 11, 11)
        self.end = datetime.date(2013, 12, 12)

        # warehouses
        self.warehouse = models.Warehouse(
            name='Warehouse1',
            show_in_report=True,
        )
        self.warehouse.save()

        self.warehouse2 = models.Warehouse(
            name='Warehouse2',
            show_in_report=True,
        )
        self.warehouse2.save()

        self.warehouse3 = models.Warehouse(
            name='Warehouse3',
            show_in_report=False,
        )
        self.warehouse3.save()

        # usage type
        self.usage_type = models.UsageType(
            name='Power consumption',
            symbol='power_consumption'
        )
        self.usage_type.save()

    def test_schema(self):
        result = PowerConsumptionSchema()
        self.assertEquals(result, OrderedDict([
            ('power_consumption_count_warehouse1', {
                'name': _('Power consumption count (warehouse1)')
            }),
            ('power_consumption_cost_warehouse1', {
                'name': _('Power consumption cost (warehouse1)'),
                'currency': True,
            }),
            ('power_consumption_count_warehouse2', {
                'name': _('Power consumption count (warehouse2)')
            }),
            ('power_consumption_cost_warehouse2', {
                'name': _('Power consumption cost (warehouse2)'),
                'currency': True,
            }),
            ('power_consumption_total_cost', {
                'name': _('Power consumption total cost'),
                'currency': True,
                'total_cost': True,
            }),
        ]))

    @mock.patch('ralph_pricing.plugins.reports.power_consumption.PowerConsumptionUsages.get_usages_and_costs')  # noqa
    def test_usages(self, get_usages_and_costs_mock):
        get_usages_and_costs_mock.side_effect = pc_get_usages_and_costs
        result = PowerConsumptionUsages(
            start=self.start,
            end=self.end,
            ventures=[]
        )
        self.assertEquals(result, {
            1: {
                'power_consumption_count_warehouse1': 123,
                'power_consumption_count_warehouse2': 43,
                'power_consumption_cost_warehouse1': D('213.22'),
                'power_consumption_cost_warehouse2': D('5656.22'),
                'power_consumption_total_cost': D('5869.44'),
            },
            2: {
                'power_consumption_count_warehouse1': 1244,
                'power_consumption_count_warehouse2': 32,
                'power_consumption_total_cost': D('2536.64'),
                'power_consumption_cost_warehouse1': D('2323.32'),
                'power_consumption_cost_warehouse2': D('213.32'),
            },
            3: {
                'power_consumption_count_warehouse1': 231,
                'power_consumption_cost_warehouse1': u'No price',
            },
            4: {
                'power_consumption_count_warehouse2': 123,
                'power_consumption_cost_warehouse2': D('123.12'),
                'power_consumption_total_cost': D('123.12'),
            }
        })

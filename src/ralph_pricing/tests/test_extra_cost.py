# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import decimal

from django.test import TestCase

from ralph_pricing.models import ExtraCostType, ExtraCost, Venture
from ralph_pricing.plugins.extra_cost import update_extra_cost


class TestExtraCostPlugin(TestCase):
    def setUp(self):
        self.date = datetime.date(2013, 01, 04)

    def get_extra_cost(self):
        """Simulated api result"""
        yield {
            'venture_id': 1,
            'venture': 'Venture1',
            'type': 'extracost_1',
            'cost': 100,
            'start': datetime.date(2013, 01, 01),
            'end': datetime.date(2013, 01, 05),
        }

    def test_sync_extra_cost(self):
        count = sum(
            update_extra_cost(data, self.date) for data in self.get_extra_cost()
        )
        self.assertEqual(count, 1)
        usage_type = ExtraCostType.objects.get(name='extracost_1')
        extra_cost = ExtraCost.objects.get(type=usage_type)
        venture = Venture.objects.get(name='Venture1')
        self.assertEqual(extra_cost.pricing_venture, venture)
        self.assertEqual(extra_cost.price, decimal.Decimal('3.278689'))

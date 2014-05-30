# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing.management.commands.pricing_statistics import Command
from ralph_pricing.tests import utils
from ralph_pricing.models import DailyUsage


class TestManagementPricingStatistics(TestCase):
    def setUp(self):
        self.usage_type = utils.get_or_create_usage_type()
        utils.get_or_create_dailyusage(type=self.usage_type)
        utils.get_or_create_dailyusage(type=self.usage_type)

    def test_get_statistics(self):
        results = Command().get_statistics(datetime.date.today())
        self.assertEqual(len(results), 1)
        self.assertEqual(results['Default0'], 2)

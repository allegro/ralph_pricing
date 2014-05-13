# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from ralph_pricing.plugins.collects.extra_cost import (
    update_extra_cost,
    extracost,
)
from ralph_pricing.models import ExtraCost, DailyExtraCost
from ralph_pricing.tests.utils import (
    get_or_create_extra_cost_type,
    get_or_create_venture,
)


class TestExtraCostCollectPlugin(TestCase):
    def setUp(self):
        self.date = datetime.date(year=2014, month=5, day=1)
        self.extracost = ExtraCost.objects.create(
            pricing_venture=get_or_create_venture(),
            type=get_or_create_extra_cost_type(),
            monthly_cost=3100,
        )

    def test_update_extra_cost(self):
        update_extra_cost(self.extracost, self.date)
        self.assertEqual(1, ExtraCost.objects.all().count())

    def test_update_extra_cost_calculate_price(self):
        update_extra_cost(self.extracost, self.date)
        self.assertEqual(100, DailyExtraCost.objects.all()[0].value)

    def test_extracost(self):
        self.assertEqual(
            (True, u'1 new extracosts', {u'today': datetime.date(2014, 5, 1)}),
            extracost(**{'today': self.date})
        )

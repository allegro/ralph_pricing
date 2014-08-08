# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from ralph_scrooge.plugins.collect.extra_cost import (
    update_extra_cost,
    extra_cost,
)
from ralph_scrooge.models import ExtraCost, DailyExtraCost
from ralph_scrooge.tests.utils.factory import (
    ExtraCostFactory,
)


class TestExtraCostCollectPlugin(TestCase):
    def setUp(self):
        self.date = datetime.date(year=2014, month=5, day=1)
        self.extracost = ExtraCostFactory.create(
            start=self.date,
            end=self.date,
        )

    def test_update_extra_cost(self):
        update_extra_cost(self.extracost, self.date)
        self.assertEqual(1, ExtraCost.objects.all().count())

    def test_update_extra_cost_calculate_price(self):
        update_extra_cost(self.extracost, self.date)
        self.assertEqual(100, DailyExtraCost.objects.all()[0].value)

    def test_extracost_when_new(self):
        self.assertEqual(
            (True, u'1 new, 0 updated, 1 total'),
            extra_cost(today=self.date)
        )

    def test_extracost_when_update(self):
        extra_cost(today=self.date)
        self.assertEqual(
            (True, u'0 new, 1 updated, 1 total'),
            extra_cost(today=self.date)
        )

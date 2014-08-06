# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from decimal import Decimal as D
from django.test import TestCase

from ralph_scrooge.plugins.reports.extracost import ExtraCostPlugin
from ralph_scrooge.tests.utils import (
    get_or_create_daily_extra_cost,
    get_or_create_venture,
    get_or_create_extra_cost_type,
    get_or_create_extra_cost,
)


class TestExtraCostReportPlugin(TestCase):
    def setUp(self):
        self.start = datetime.date.today()
        self.end = datetime.date.today() + datetime.timedelta(days=1)
        self.venture = get_or_create_venture()
        self.type = get_or_create_extra_cost_type()
        self.extra_cost = get_or_create_extra_cost(
            mode=1,
            start=self.start,
            end=self.end,
            pricing_venture=self.venture,
            type=self.type,
        )
        self.value = D(100)
        self.daily_extra_cost = get_or_create_daily_extra_cost(
            venture=self.venture,
            type=self.type,
            value=self.value,
        )

    def test_get_extra_costs_daily_imprint(self):
        self.assertEqual(
            self.venture.id,
            ExtraCostPlugin.get_extra_costs_daily_imprint(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['pricing_venture']
        )
        self.assertEqual(
            self.type.id,
            ExtraCostPlugin.get_extra_costs_daily_imprint(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['type']
        )
        self.assertEqual(
            self.value,
            ExtraCostPlugin.get_extra_costs_daily_imprint(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['total_cost']
        )
        self.assertEqual(
            self.value,
            ExtraCostPlugin.get_extra_costs_daily_imprint(
                self.start,
                self.end,
                [self.venture],
            )[1]
        )

    def test_get_extra_costs_monthly_cost(self):
        self.assertEqual(
            self.venture.id,
            ExtraCostPlugin.get_extra_costs_monthly_cost(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['pricing_venture']
        )
        self.assertEqual(
            self.type,
            ExtraCostPlugin.get_extra_costs_monthly_cost(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['type']
        )
        self.assertEqual(
            self.value,
            ExtraCostPlugin.get_extra_costs_monthly_cost(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['total_cost']
        )
        self.assertEqual(
            self.value,
            ExtraCostPlugin.get_extra_costs_monthly_cost(
                self.start,
                self.end,
                [self.venture],
            )[1]
        )

    def test_get_extra_costs(self):
        self.assertEqual(
            self.venture.id,
            ExtraCostPlugin.get_extra_costs(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['pricing_venture']
        )
        self.assertEqual(
            self.type.id,
            ExtraCostPlugin.get_extra_costs(
                self.start,
                self.end,
                [self.venture],
            )[0][0]['type']
        )
        self.assertEqual(
            self.value * 2,
            ExtraCostPlugin.get_extra_costs(
                self.start,
                self.end,
                [self.venture],
            )[1]
        )

    def test_costs(self):
        self.assertEqual(
            self.value,
            ExtraCostPlugin.costs(
                self.start,
                self.end,
                [self.venture],
            )[1]['extra_cost_{}'.format(self.type.id)]
        )
        self.assertEqual(
            self.value * 2,
            ExtraCostPlugin.costs(
                self.start,
                self.end,
                [self.venture],
            )[1]['extra_costs_total']
        )

    def test_schema(self):
        self.assertEqual(
            True,
            ExtraCostPlugin.schema()[
                'extra_cost_{}'.format(self.type.id)
            ]['currency']
        )
        self.assertEqual(
            self.type.name,
            ExtraCostPlugin.schema()[
                'extra_cost_{}'.format(self.type.id)
            ]['name']
        )
        self.assertEqual(
            True,
            ExtraCostPlugin.schema()['extra_costs_total']['total_cost']
        )
        self.assertEqual(
            'Extra Costs Total',
            ExtraCostPlugin.schema()['extra_costs_total']['name']
        )

    def test_total_cost(self):
        self.assertEqual(
            self.value * 2,
            ExtraCostPlugin.total_cost(
                self.start,
                self.end,
                [self.venture]
            )
        )

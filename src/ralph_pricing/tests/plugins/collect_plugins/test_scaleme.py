#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.conf import settings
from django.test import TestCase
from ralph_pricing.models import DailyUsage, UsageType, Venture
from ralph_pricing.plugins.collects.scaleme import (
    scaleme as scaleme_runner
)


def mock_get_ventures_capacities(date, url):
    return {
        "test_venture1": {
            "cache": 7878,
            "backend": 987987,
        },
        "test_venture2": {
            "cache": 666999,
            "backend": 12346699,
        },
    }


class TestScaleme(TestCase):
    def setUp(self):
        self.venture_1 = Venture(
            name='Test Venture1',
            symbol='test_venture1',
            venture_id='1',
        )
        self.venture_1.save()
        self.venture_2 = Venture(
            name='Test Venture2',
            symbol='test_venture2',
            venture_id='2',
        )
        self.venture_2.save()
        self.venture_3 = Venture(
            name='Test Venture3',
            symbol='test_venture3',
            venture_id='3',
        )
        self.venture_3.save()

    def test_set_usages(self):
        """Scaleme usages Test Case"""
        settings.SCALEME_API_URL = "/"
        with mock.patch(
            'ralph_pricing.plugins.collects.scaleme.get_ventures_capacities'
        ) as get_ventures_capacities:
            get_ventures_capacities.side_effect = mock_get_ventures_capacities
            status, message, args = scaleme_runner(
                today=datetime.datetime.today()
            )
            self.assertTrue(status)
            usages = DailyUsage.objects.all()
            self.assertEqual(usages.count(), 4)

            usage_backend = UsageType.objects.get(
                name='Scaleme transforming an image 10000 events',
            )
            usage_cache = UsageType.objects.get(
                name='Scaleme serving image from cache 10000 events',
            )

            usages_venture1 = DailyUsage.objects.filter(
                pricing_venture=self.venture_1,
            )
            usages_venture2 = DailyUsage.objects.filter(
                pricing_venture=self.venture_2,
            )
            usages_venture3 = DailyUsage.objects.filter(
                pricing_venture=self.venture_3,
            )

            self.assertEqual(usages_venture1.count(), 2)
            usage_backend_venture1 = usages_venture1.filter(type=usage_backend)
            usage_cache_venture1 = usages_venture1.filter(type=usage_cache)
            self.assertEqual(usage_backend_venture1[0].value, 987987)
            self.assertEqual(usage_cache_venture1[0].value, 7878)

            self.assertEqual(usages_venture2.count(), 2)
            usage_backend_venture2 = usages_venture2.filter(type=usage_backend)
            usage_cache_venture2 = usages_venture2.filter(type=usage_cache)
            self.assertEqual(usage_backend_venture2[0].value, 12346699)
            self.assertEqual(usage_cache_venture2[0].value, 666999)

            self.assertEqual(usages_venture3.count(), 0)

    def test_fail_plugin(self):
        """Testing not configured plugin"""
        with mock.patch(
            'ralph_pricing.plugins.collects.scaleme.get_ventures_capacities'
        ) as get_ventures_capacities:
            get_ventures_capacities.side_effect = mock_get_ventures_capacities
            status, message, args = scaleme_runner(
                today=datetime.datetime.today(),
            )
            self.assertFalse(status)

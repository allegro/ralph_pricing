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

from ralph_pricing.models import DailyUsage, Venture
from ralph_pricing.plugins.collects.hamster import (
    hamster as hamster_runner,
)


def mock_get_venture_capacity(venture_symbol, url):
    if venture_symbol == 'test_venture1':
        capacity = 2131231233.0
    elif venture_symbol == 'test_venture2':
        capacity = 4234233423.0
    else:
        capacity = 0
    return capacity


class TestHamster(TestCase):
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
        """ Hamster usages Test Case """
        # fake setting need to run plugin
        settings.HAMSTER_API_URL = "/"
        with mock.patch(
            'ralph_pricing.plugins.collects.hamster.get_venture_capacity'
        ) as get_venture_capacity:
            get_venture_capacity.side_effect = mock_get_venture_capacity
            status, message, args = hamster_runner(
                today=datetime.datetime.today()
            )
            self.assertTrue(status)

            usages = DailyUsage.objects.all()
            self.assertEqual(len(usages), 2)

            usage_venture1 = DailyUsage.objects.get(
                pricing_venture=self.venture_1
            )
            usage_venture2 = DailyUsage.objects.get(
                pricing_venture=self.venture_2
            )
            self.assertEqual(
                usage_venture1.value, 2131231233.0 / (1024 * 1024)
            )
            self.assertEqual(
                usage_venture2.value, 4234233423.0 / (1024 * 1024)
            )

    def test_fail_plugin(self):
        """ Testing not configured plugin """
        with mock.patch(
            'ralph_pricing.plugins.collects.hamster.get_venture_capacity'
        ) as get_venture_capacity:
            get_venture_capacity.side_effect = mock_get_venture_capacity
            status, message, args = hamster_runner(
                today=datetime.datetime.today()
            )
            self.assertFalse(status)

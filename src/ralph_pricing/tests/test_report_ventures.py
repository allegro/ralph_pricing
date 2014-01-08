# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.views.ventures import AllVentures, TopVentures


class TestReportVentures(TestCase):
    def setUp(self):
        self.day = day = datetime.date(2013, 4, 25)

        # ventures
        venture = models.Venture(venture_id=3, name='a', is_active=True)
        venture.save()
        subventure = models.Venture(
            venture_id=2,
            parent=venture,
            name='b',
            is_active=False,
        )
        subventure.save()

        # devices (assets)
        device = models.Device(
            device_id=3,
            asset_id=5,
        )
        device.save()
        daily = models.DailyDevice(
            pricing_device=device,
            date=day,
            name='ziew',
            price='1337',
            pricing_venture=venture,
        )
        daily.save()

        other_device = models.Device(
            device_id=2,
            asset_id=3,
        )
        other_device.save()
        other_daily = models.DailyDevice(
            pricing_device=other_device,
            date=day,
            name='ziew',
            price='833833',
            pricing_venture=subventure,
        )
        other_daily.save()

        # usages
        usage_type = models.UsageType(name='waciki')
        usage_type.save()
        daily_usage = models.DailyUsage(
            type=usage_type,
            value=32,
            date=day,
            pricing_venture=venture,
        )
        daily_usage.save()

        # extra costs
        extra_cost_type = models.ExtraCostType(name='waciki')
        extra_cost_type.save()
        extra_cost = models.ExtraCost(
            pricing_venture=venture,
            start=day,
            end=day,
            type=extra_cost_type,
            price='65535',
        )
        extra_cost.save()

    def test_top_ventures(self):
        view = TopVentures()
        day = self.day
        for progress, data in view.get_data(day, day, show_in_ralph=False):
            pass
        self.assertEquals(
            data,
            [
                [
                    3,                 # id
                    'a',               # path
                    True,              # show_in_ralph
                    '',                # department
                    '',                # business segment
                    '',                # Profit center
                    2.0,               # assets count
                    '835 170.00 PLN',  # assets price
                    '0.00 PLN',        # assets cost
                    32.0,              # usage count
                    '0.00 PLN',        # usage price
                    '65 535.00 PLN',   # extra cost
                ],
            ],
        )

    def test_all_ventures(self):
        view = AllVentures()
        day = self.day
        for progress, data in view.get_data(day, day, show_in_ralph=False):
            pass
        self.assertEquals(
            data,
            [
                [
                    3,
                    'a',
                    True,  # show_in_ralph
                    '',
                    '',
                    '',
                    1.0,
                    '1 337.00 PLN',
                    '0.00 PLN',
                    32.0,
                    'NO PRICE',
                    '65 535.00 PLN',
                ],
                [
                    2,
                    'a/b',
                    False,  # show_in_ralph
                    '',
                    '',
                    '',
                    1.0,
                    '833 833.00 PLN',
                    '0.00 PLN',
                    0,
                    '0.00 PLN',
                    '0.00 PLN',
                ],
            ],
        )

    def test_all_ventures_active(self):
        view = AllVentures()
        day = self.day
        for progress, data in view.get_data(day, day, show_in_ralph=True):
            pass
        self.assertEquals(
            data,
            [
                [
                    3,
                    'a',
                    True,  # show_in_ralph
                    '',
                    '',
                    '',
                    1.0,
                    '1 337.00 PLN',
                    '0.00 PLN',
                    32.0,
                    'NO PRICE',
                    '65 535.00 PLN',
                ],
            ],
        )

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing.models import DailyPart
from ralph_pricing.plugins.collects.assets_part import update_assets_parts


class TestAssetPlugin(TestCase):
    def setUp(self):
        self.today = datetime.date.today()

    def get_asset_part(self):
        """Simulated api result"""
        yield {
            'asset_id': 1123,
            'ralph_id': 113,
            'model': 'Noname SSD',
            'price': 130,
            'is_deprecated': True,
            'deprecation_rate': 0,
        }

    def test_sync_asset_device_part(self):
        count = sum(
            update_assets_parts(
                data,
                self.today
            ) for data in self.get_asset_part()
        )
        part = DailyPart.objects.get(asset_id=1123)
        self.assertEqual(count, 1)
        self.assertEqual(part.is_deprecated, True)
        self.assertEqual(part.name, 'Noname SSD')
        self.assertEqual(part.price, 130)

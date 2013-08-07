# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing.models import Device, DailyDevice
from ralph_pricing.plugins.assets import update_assets


class TestAssetPlugin(TestCase):
    def setUp(self):
        self.today = datetime.date.today()

    def get_asset(self):
        """Simulated api result"""
        yield {
            'asset_id': 1123,
            'ralph_id': 13342,
            'slots': 10.0,
            'price': 100,
            'is_deprecated': True,
            'sn': '1234-1234-1234-1234',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }

    def test_sync_asset_device(self):
        count = sum(
            update_assets(data, self.today) for data in self.get_asset()
        )
        self.assertEqual(count, 1)
        device = Device.objects.get(device_id=13342)
        self.assertEqual(device.device_id, 13342)
        self.assertEqual(device.asset_id, 1123)
        self.assertEqual(device.slots, 10.0)
        self.assertEqual(device.sn, '1234-1234-1234-1234')
        self.assertEqual(device.barcode, '4321-4321-4321-4321')

    def test_sync_asset_daily(self):
        count = sum(
            update_assets(data, self.today) for data in self.get_asset()
        )
        self.assertEqual(count, 1)
        daily = DailyDevice.objects.get(date=self.today)
        self.assertEqual(daily.is_deprecated, True)
        self.assertEqual(daily.price, 100)
        self.assertEqual(daily.pricing_device_id, 1)
        self.assertEqual(daily.date, self.today)

    def test_sync_asset_device_without_ralph_id(self):
        data = yield {
            'asset_id': 1123,
            'ralph_id': None,
            'slots': 10.0,
            'price': 100,
            'is_deprecated': True,
            'sn': '1234-1234-1234-1234',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }
        count = sum(update_assets(item, self.today) for item in data)
        self.assertFalse(count > 0)

    def test_sync_asset_device_update(self):
        data = yield {
            'asset_id': 1123,
            'ralph_id': 123,
            'slots': 10.0,
            'price': 100,
            'is_deprecated': True,
            'sn': '1234-1234-1234-1234',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }
        count = sum(update_assets(item, self.today) for item in data)
        self.assertFalse(count == 1)
        device = Device.objects.get(device_id=123)
        self.assertEqual(device.sn, '1234-1234-1234-1234')

        data = yield {
            'asset_id': 1123,
            'ralph_id': 123,
            'slots': 10.0,
            'price': 100,
            'is_deprecated': True,
            'sn': '5555-5555-5555-5555',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }
        device = Device.objects.get(device_id=123)
        self.assertEqual(device.sn, '5555-5555-5555-5555')





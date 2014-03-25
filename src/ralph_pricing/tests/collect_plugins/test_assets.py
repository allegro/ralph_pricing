# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing.models import (
    Device,
    DailyDevice,
    DailyUsage,
    UsageType,
    Warehouse,
)
from ralph_pricing.plugins.collects.assets import update_assets


class TestAssetPlugin(TestCase):
    def setUp(self):
        self.today = datetime.date.today()

        self.core_usage_type, created = UsageType.objects.get_or_create(
            name="Physical CPU cores",
            symbol='physical_cpu_cores',
            average=True,
        )
        self.core_usage_type.save()

        self.power_consumption_usage_type, created = \
            UsageType.objects.get_or_create(
                name="Power consumption",
                symbol='power_consumption',
                by_warehouse=True,
                by_cost=True,
            )
        self.power_consumption_usage_type.save()

        self.height_of_device_usage_type, created = \
            UsageType.objects.get_or_create(
                name="Height of Device",
                symbol='height_of_device',
                by_warehouse=True,
                by_cost=True,
            )
        self.height_of_device_usage_type.save()

        self.warehouse, created = Warehouse.objects.get_or_create(
            name="Sample warehouse"
        )
        self.warehouse.save()

    def _get_asset(self):
        """Simulated api result"""
        yield {
            'asset_id': 1123,
            'ralph_id': 13342,
            'slots': 10.0,
            'power_consumption': 1000,
            'height_of_device': 10.00,
            'price': 100,
            'is_deprecated': True,
            'sn': '1234-1234-1234-1234',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
            'is_blade': True,
            'venture_id': 12,
            'cores_count': 8,
            'warehouse_id': self.warehouse.id,
        }

    def test_sync_asset_device(self):
        count = sum(
            update_assets(
                data,
                self.today,
                {
                    'core': self.core_usage_type,
                    'power_consumption': self.power_consumption_usage_type,
                    'height_of_device': self.height_of_device_usage_type,
                },
            ) for data in self._get_asset()
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
            update_assets(
                data,
                self.today,
                {
                    'core': self.core_usage_type,
                    'power_consumption': self.power_consumption_usage_type,
                    'height_of_device': self.height_of_device_usage_type,
                },
            ) for data in self._get_asset()
        )
        self.assertEqual(count, 1)
        daily = DailyDevice.objects.get(date=self.today)
        self.assertEqual(daily.is_deprecated, True)
        self.assertEqual(daily.price, 100)
        self.assertEqual(daily.pricing_device_id, 1)

    def test_sync_asset_dailyusage_core(self):
        count = sum(
            update_assets(
                data,
                self.today,
                {
                    'core': self.core_usage_type,
                    'power_consumption': self.power_consumption_usage_type,
                    'height_of_device': self.height_of_device_usage_type,
                },
            ) for data in self._get_asset()
        )
        self.assertEqual(count, 1)
        usage = DailyUsage.objects.get(
            date=self.today,
            type=self.core_usage_type,
        )
        self.assertEqual(usage.value, 8)
        self.assertEqual(usage.pricing_device_id, 1)
        self.assertEqual(usage.warehouse_id, None)
        self.assertEqual(usage.type, self.core_usage_type)

    def test_sync_asset_dailyusage_power_consumption(self):
        count = sum(
            update_assets(
                data,
                self.today,
                {
                    'core': self.core_usage_type,
                    'power_consumption': self.power_consumption_usage_type,
                    'height_of_device': self.height_of_device_usage_type,
                },
            ) for data in self._get_asset()
        )
        self.assertEqual(count, 1)
        usage = DailyUsage.objects.get(
            date=self.today,
            type=self.power_consumption_usage_type,
        )
        self.assertEqual(usage.value, 1000)
        self.assertEqual(usage.pricing_device_id, 1)
        self.assertEqual(usage.warehouse_id, self.warehouse.id)

        usage = DailyUsage.objects.get(
            date=self.today,
            type=self.core_usage_type,
        )
        self.assertEqual(usage.value, 8)

        usage = DailyUsage.objects.get(
            date=self.today,
            type=self.height_of_device_usage_type,
        )
        self.assertEqual(usage.value, 10.00)

    def test_sync_asset_device_without_ralph_id(self):
        data = yield {
            'asset_id': 1123,
            'ralph_id': None,
            'slots': 10.0,
            'power_consumption': 1000,
            'price': 100,
            'is_deprecated': True,
            'sn': '1234-1234-1234-1234',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }
        count = sum(
            update_assets(
                item,
                self.today,
                self.core_usage_type,
                self.power_consumption_usage_type,
            ) for item in data
        )
        self.assertFalse(count > 0)

    def test_sync_asset_device_update(self):
        data = yield {
            'asset_id': 1123,
            'ralph_id': 123,
            'slots': 10.0,
            'power_consumption': 1000,
            'price': 100,
            'is_deprecated': True,
            'sn': '1234-1234-1234-1234',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }
        count = sum(
            update_assets(
                item,
                self.today,
                self.core_usage_type,
                self.power_consumption_usage_type,
            ) for item in data
        )
        self.assertFalse(count == 1)
        device = Device.objects.get(device_id=123)
        self.assertEqual(device.sn, '1234-1234-1234-1234')

        data = yield {
            'asset_id': 1123,
            'ralph_id': 123,
            'slots': 10.0,
            'power_consumption': 1000,
            'price': 100,
            'is_deprecated': True,
            'sn': '5555-5555-5555-5555',
            'barcode': '4321-4321-4321-4321',
            'deprecation_rate': 0,
        }
        device = Device.objects.get(device_id=123)
        self.assertEqual(device.sn, '5555-5555-5555-5555')

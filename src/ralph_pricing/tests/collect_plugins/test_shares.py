# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from django.test import TestCase

from ralph_pricing.models import DailyUsage, UsageType
from ralph_pricing.plugins.collects.shares import (
    update_usage,
    update,
)
from ralph_pricing.tests.utils import (
    get_or_create_device,
    get_or_create_venture,
    get_or_create_dailydevice
)


class TestSharesPlugin(TestCase):
    def setUp(self):
        self.venture = get_or_create_venture()
        self.venture2 = get_or_create_venture()
        self.device = get_or_create_device(device_id=1)
        self.usage_type = UsageType(
            name='Usage1',
            symbol='ut1',
        )
        self.usage_type.save()
        self.today = date.today()

    def test_update_usage(self):
        update_usage(self.device, self.venture, self.usage_type, self.today, 8)

        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.all()[0]
        self.assertEqual(daily_usage.pricing_venture, self.venture)
        self.assertEqual(daily_usage.pricing_device, self.device)
        self.assertEqual(daily_usage.value, 8)
        self.assertEqual(daily_usage.date.date(), self.today)
        self.assertEqual(daily_usage.type, self.usage_type)

    def test_update_usage_append(self):
        update_usage(self.device, self.venture, self.usage_type, self.today, 8)
        update_usage(self.device, self.venture, self.usage_type, self.today, 8)

        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.all()[0]
        self.assertEqual(daily_usage.pricing_venture, self.venture)
        self.assertEqual(daily_usage.pricing_device, self.device)
        self.assertEqual(daily_usage.value, 16)
        self.assertEqual(daily_usage.date.date(), self.today)
        self.assertEqual(daily_usage.type, self.usage_type)

    def test_update(self):
        data = {
            'mount_device_id': self.device.device_id,
            'size': 10
        }
        get_or_create_dailydevice(
            date=self.today,
            device=self.device,
            venture=self.venture,
        )
        result = update(data, self.today, self.usage_type, None)

        self.assertTrue(result)
        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.all()[0]
        self.assertEqual(daily_usage.pricing_venture, self.venture)
        self.assertEqual(daily_usage.pricing_device, self.device)
        self.assertEqual(daily_usage.value, 10)
        self.assertEqual(daily_usage.date.date(), self.today)
        self.assertEqual(daily_usage.type, self.usage_type)

    def test_update_without_device_id(self):
        data = {
            'mount_device_id': None,
            'size': 10
        }
        result = update(data, self.today, self.usage_type, None)
        self.assertFalse(result)

    def test_update_device_not_found(self):
        data = {
            'mount_device_id': self.device.device_id + 1,
            'size': 10
        }
        result = update(data, self.today, self.usage_type, None)
        self.assertFalse(result)

    def test_update_dailydevice_not_found(self):
        data = {
            'mount_device_id': self.device.device_id,
            'size': 10
        }
        result = update(data, self.today, self.usage_type, None)
        self.assertFalse(result)

    def test_update_device_not_found_unknown_venture(self):
        data = {
            'mount_device_id': self.device.device_id + 1,
            'size': 10
        }
        result = update(data, self.today, self.usage_type, self.venture2)

        self.assertTrue(result)
        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.all()[0]
        self.assertEqual(daily_usage.pricing_venture, self.venture2)
        self.assertIsNone(daily_usage.pricing_device)
        self.assertEqual(daily_usage.value, 10)
        self.assertEqual(daily_usage.date.date(), self.today)
        self.assertEqual(daily_usage.type, self.usage_type)

    def test_update_dailydevice_not_found_unknown_venture(self):
        data = {
            'mount_device_id': self.device.device_id,
            'size': 10
        }
        result = update(data, self.today, self.usage_type, self.venture2)

        self.assertTrue(result)
        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.all()[0]
        self.assertEqual(daily_usage.pricing_venture, self.venture2)
        self.assertEqual(daily_usage.pricing_device, self.device)
        self.assertEqual(daily_usage.value, 10)
        self.assertEqual(daily_usage.date.date(), self.today)
        self.assertEqual(daily_usage.type, self.usage_type)

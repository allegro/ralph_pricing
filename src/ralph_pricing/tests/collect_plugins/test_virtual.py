# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, date

from django.test import TestCase

from ralph_pricing.models import UsageType, DailyUsage, Device
from ralph_pricing.plugins.collects.virtual import (
    get_or_create_usages,
    update_usage,
    update,
)
from ralph_pricing.tests.utils import (
    get_or_create_device,
    get_or_create_venture,
)


class TestAssetPlugin(TestCase):
    def setUp(self):
        self.device = get_or_create_device()
        self.venture = get_or_create_venture()

    def _get_usages(self):
        usage_names = {
            'virtual_cores': 'Virtual CPU cores',
            'virtual_disk': 'Virtual disk MB',
            'virtual_memory': 'Virtual memory MB',
        }

        return get_or_create_usages(usage_names)

    def test_get_usages(self):
        usages = self._get_usages()
        usages_from_database = UsageType.objects.all().order_by('name')

        self.assertEqual(usages['virtual_cores'], usages_from_database[0])
        self.assertEqual(usages['virtual_disk'], usages_from_database[1])
        self.assertEqual(usages['virtual_memory'], usages_from_database[2])

    def test_update_usage_when_there_is_no_value(self):
        update_usage(
            self.device,
            self.venture,
            self._get_usages()['virtual_cores'],
            datetime.today(),
            None,
        )
        self.assertItemsEqual(DailyUsage.objects.all(), [])

    def test_update_usage(self):
        usages = self._get_usages()
        update_usage(
            self.device,
            self.venture,
            usages['virtual_cores'],
            date.today(),
            1,
        )

        daily_usages = DailyUsage.objects.all()
        self.assertEqual(daily_usages.count(), 1)
        self.assertEqual(daily_usages[0].pricing_device, self.device)
        self.assertEqual(daily_usages[0].pricing_venture, self.venture)
        self.assertEqual(daily_usages[0].type, usages['virtual_cores'])
        self.assertEqual(daily_usages[0].value, 1)

    def test_update_when_device_id_is_none(self):
        update({}, self._get_usages(), date.today())

        self.assertItemsEqual(Device.objects.all(), [self.device])

    def test_update_when_venture_id_is_none(self):
        data = {
            'device_id': 1,
            'virtual_cores': 1,
            'virtual_disk': 1,
            'virtual_memory': 1,
        }
        update(data, self._get_usages(), date.today())

        daily_usages = DailyUsage.objects.all()
        self.assertEqual(daily_usages.count(), 0)
        for daily_usage in daily_usages:
            self.assertEqual(daily_usage.pricing_venture, None)

    def test_update(self):
        data = {
            'device_id': 1,
            'venture_id': 1,
            'virtual_cores': 1,
            'virtual_disk': 1,
            'virtual_memory': 1,
        }
        update(data, self._get_usages(), date.today())

        daily_usages = DailyUsage.objects.all()
        self.assertEqual(daily_usages.count(), 3)
        for daily_usage in daily_usages:
            self.assertEqual(daily_usage.pricing_venture.venture_id, 1)

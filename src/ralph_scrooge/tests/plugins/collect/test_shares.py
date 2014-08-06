# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings

from ralph_scrooge.models import DailyUsage, UsageType
from ralph_scrooge.plugins.collect import share

from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyPricingObjectFactory,
    UsageTypeFactory,
)


class TestSharesPlugin(TestCase):
    def setUp(self):
        self.date = date.today()
        self.data = {
            'size': 100,
            'mount_device_id': 1,
            'storage_device_id': 1,
            'label': 'test share',
        }
        self.asset_info = AssetInfoFactory.create(
            device_id=self.data['mount_device_id']
        )
        self.usage_type = UsageTypeFactory.create()

    def test_update_usage(self):
        DailyPricingObjectFactory.create(
            pricing_object=self.asset_info,
            date=self.date,
        )
        share.update_usage(
            self.asset_info,
            self.usage_type,
            self.data,
            self.date,
        )
        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.all()[0]
        self.assertEqual(daily_usage.value, self.data['size'])
        self.assertEqual(daily_usage.type, self.usage_type)
        self.assertEqual(daily_usage.service, self.asset_info.service)

    def test_update_when_unknown_mount_device_id_error(self):
        self.data['mount_device_id'] = None
        self.assertRaises(
            share.UnknownMountDeviceIdError,
            share.update,
            usage_type=self.usage_type,
            data=self.data,
            date=self.date,
        )

    def test_update_when_asset_info_does_not_exist_error(self):
        self.data['mount_device_id'] = 2
        self.assertRaises(
            share.AssetInfoDoesNotExistError,
            share.update,
            usage_type=self.usage_type,
            data=self.data,
            date=self.date,
        )

    @patch.object(share, 'update_usage', lambda x, y, z, k: True)
    def test_update(self):
        self.assertEqual(
            share.update(self.usage_type, self.data, self.date),
            True,
        )

    def test_get_usage(self):
        self.assertEqual(
            share.get_usage('Test usage'),
            UsageType.objects.all()[1]
        )

    @patch.object(share, 'logger', MagicMock())
    @patch.object(settings, 'SHARE_SERVICE_CI_UID', {'group': ['ci_uid']})
    def test_share_when_unknown_mount_device_id_error(self):
        share.get_shares = lambda service_ci_uid, include_virtual: [self.data]
        self.data['mount_device_id'] = None
        self.assertEqual(
            share.share(today=self.date),
            (True, 'None new, 0 updated, 1 total'),
        )

    @patch.object(share, 'logger', MagicMock())
    @patch.object(settings, 'SHARE_SERVICE_CI_UID', {'group': ['ci_uid']})
    def test_share_when_asset_info_does_not_exist_error(self):
        share.get_shares = lambda service_ci_uid, include_virtual: [self.data]
        self.data['mount_device_id'] = 2
        self.assertEqual(
            share.share(today=self.date),
            (True, 'None new, 0 updated, 1 total'),
        )

    @patch.object(share, 'logger', MagicMock())
    @patch.object(settings, 'SHARE_SERVICE_CI_UID', {'group': ['ci_uid']})
    def test_share(self):
        DailyPricingObjectFactory.create(
            pricing_object=self.asset_info,
            date=self.date,
        )
        share.get_shares = lambda service_ci_uid, include_virtual: [self.data]
        self.assertEqual(
            share.share(today=self.date),
            (True, 'None new, 1 updated, 1 total'),
        )

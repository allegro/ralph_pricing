# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.models import DailyUsage, UsageType
from ralph_scrooge.plugins.collect import share
from ralph_scrooge.tests.utils.factory import (
    AssetInfoFactory,
    DailyAssetInfoFactory,
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
        DailyAssetInfoFactory.create(
            pricing_object=self.asset_info,
            asset_info=self.asset_info,
            date=self.date,
        )
        share.update_usage(
            self.asset_info,
            self.usage_type,
            self.data,
            self.date,
        )
        self.assertEqual(DailyUsage.objects.count(), 1)
        daily_usage = DailyUsage.objects.get()
        self.assertEqual(daily_usage.value, self.data['size'])
        self.assertEqual(daily_usage.type, self.usage_type)
        self.assertEqual(
            daily_usage.service_environment,
            self.asset_info.service_environment
        )

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
        asset_info = AssetInfoFactory.build()
        self.data['mount_device_id'] = asset_info.device_id
        self.assertRaises(
            share.AssetInfoDoesNotExistError,
            share.update,
            usage_type=self.usage_type,
            data=self.data,
            date=self.date,
        )

    @patch.object(share, 'update_usage', lambda *args, **kwargs: True)
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

    @override_settings(SHARE_SERVICES={'group': ['ci_uid']})
    def test_share_when_unknown_mount_device_id_error(self):
        share.get_shares = lambda service_uid, include_virtual: [self.data]
        self.data['mount_device_id'] = None
        self.assertEqual(
            share.share(today=self.date),
            (True, 'None new, 0 updated, 1 total'),
        )

    @override_settings(SHARE_SERVICES={'group': ['ci_uid']})
    def test_share_when_asset_info_does_not_exist_error(self):
        share.get_shares = lambda service_uid, include_virtual: [self.data]
        self.data['mount_device_id'] = 2
        self.assertEqual(
            share.share(today=self.date),
            (True, 'None new, 0 updated, 1 total'),
        )

    @override_settings(SHARE_SERVICES={'group': ['ci_uid']})
    def test_share(self):
        DailyAssetInfoFactory.create(
            pricing_object=self.asset_info,
            asset_info=self.asset_info,
            date=self.date,
        )
        share.get_shares = lambda service_uid, include_virtual: [self.data]
        self.assertEqual(
            share.share(today=self.date),
            (True, 'None new, 1 updated, 1 total'),
        )

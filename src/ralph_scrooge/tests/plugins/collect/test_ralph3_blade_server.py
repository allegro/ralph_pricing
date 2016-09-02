# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase
from django.test.utils import override_settings

from ralph_scrooge.models import DailyUsage
from ralph_scrooge.plugins.collect.ralph3_blade_server import (
    AssetInfoNotFoundError,
    DailyAssetInfoNotFoundError,
    ralph3_blade_server as blade_server_plugin,
    get_usage_type,
    update_blade_server,
    update_usage,
)
from ralph_scrooge.tests.utils.factory import AssetInfoFactory


class TestBladeServerCollectPlugin(TestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.blade_server_usage_type = get_usage_type()
        self.data = [
            {
                'id': 10,
                '__str__': 'data center asset: 10',
                'status': 'free',
            },
            {
                'id': 20,
                '__str__': 'data center asset: 20',
                'status': 'in use',
            },
            {
                'id': 30,
                '__str__': 'data center asset: 30',
                'status': 'in use',
            },
            {
                'id': 40,
                '__str__': 'data center asset: 40',
                'status': 'in use',
            },
            {
                'id': 50,
                '__str__': 'data center asset: 50',
                'status': 'liquidated',
            },
        ]
        ai = AssetInfoFactory(ralph3_asset_id=10)
        self.dai = ai.get_daily_pricing_object(date=self.today)

    def test_update_usage(self):
        self.assertTrue(update_usage(
            self.dai,
            self.today,
            1,
            self.blade_server_usage_type,
        ))
        self.assertEquals(
            self.blade_server_usage_type.dailyusage_set.count(),
            1
        )
        daily_usage = self.blade_server_usage_type.dailyusage_set.all()[0]
        self.assertEquals(daily_usage.date, self.today)
        self.assertEquals(
            daily_usage.service_environment,
            self.dai.service_environment
        )
        self.assertEquals(daily_usage.type, self.blade_server_usage_type)
        self.assertEquals(daily_usage.value, 1)

        # update
        self.assertFalse(update_usage(
            self.dai,
            self.today,
            2,
            self.blade_server_usage_type,
        ))
        self.assertEquals(
            self.blade_server_usage_type.dailyusage_set.count(),
            1
        )
        daily_usage = self.blade_server_usage_type.dailyusage_set.all()[0]
        self.assertEquals(daily_usage.value, 2)

    @mock.patch('ralph_scrooge.plugins.collect.ralph3_blade_server.update_usage')  # noqa
    def test_update_blade_server(self, update_usage_mock):
        update_usage_mock.return_value = True
        self.assertTrue(update_blade_server(
            self.data[0],
            self.today,
            self.blade_server_usage_type
        ))
        update_usage_mock.assert_called_with(
            self.dai,
            self.today,
            1,
            self.blade_server_usage_type,
        )

    def test_update_blade_server_no_daily_asset_info(self):
        AssetInfoFactory(ralph3_asset_id=20)
        with self.assertRaises(DailyAssetInfoNotFoundError):
            update_blade_server(
                self.data[1],
                self.today + datetime.timedelta(days=1),
                self.blade_server_usage_type
            )

    def test_update_blade_server_no_asset_info(self):
        with self.assertRaises(AssetInfoNotFoundError):
            update_blade_server(
                self.data[2],
                self.today,
                self.blade_server_usage_type
            )

    @override_settings(RALPH3_BLADE_SERVER_CATEGORY_ID=111)
    @mock.patch('ralph_scrooge.plugins.collect.ralph3_blade_server.get_from_ralph')  # noqa
    def test_batch_update(self, get_from_ralph_mock):
        # assetinfo without daily asset info
        ai = AssetInfoFactory(ralph3_asset_id=20)
        dai = ai.get_daily_pricing_object(self.today)
        DailyUsage.objects.get_or_create(
            date=self.today,
            type=get_usage_type(),
            daily_pricing_object=dai,
            service_environment=dai.service_environment,
        )
        get_from_ralph_mock.return_value = self.data
        # 2 errors: AssetInfoDoesNotExist and DailyAssetInfoDoesNotExist
        self.assertEquals(
            blade_server_plugin(today=self.today),
            (True, '1 new Blade Servers usages, 1 updated, 2 errors, 4 total')
        )

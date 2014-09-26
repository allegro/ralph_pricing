# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase

from ralph_scrooge.plugins.collect.blade_server import (
    AssetInfoNotFoundError,
    DailyAssetInfoNotFoundError,
    blade_server as blade_server_plugin,
    get_usage_type,
    update_blade_server,
    update_usage,
)
from ralph_scrooge.tests.utils.factory import DailyAssetInfoFactory
from ralph_scrooge.tests.plugins.collect.samples.blade_server import (
    SAMPLE_BLADE_SERVER
)


class TestBladeServerCollectPlugin(TestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.blade_server_usage_type = get_usage_type()

    def test_update_usage(self):
        daily_asset_info = DailyAssetInfoFactory(date=self.today)
        self.assertTrue(update_usage(
            daily_asset_info,
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
            daily_asset_info.service_environment
        )
        self.assertEquals(daily_usage.type, self.blade_server_usage_type)
        self.assertEquals(daily_usage.value, 1)

        # update
        self.assertFalse(update_usage(
            daily_asset_info,
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

    @mock.patch('ralph_scrooge.plugins.collect.blade_server.update_usage')
    def test_update_blade_server(self, update_usage_mock):
        update_usage_mock.return_value = True
        daily_asset_info = DailyAssetInfoFactory(date=self.today)
        self.assertTrue(update_blade_server(
            {'id': 1, 'device_id': daily_asset_info.asset_info.device_id},
            self.today,
            self.blade_server_usage_type
        ))
        update_usage_mock.assert_called_with(
            daily_asset_info,
            self.today,
            1,
            self.blade_server_usage_type,
        )

    def test_update_blade_server_no_daily_asset_info(self):
        daily_asset_info = DailyAssetInfoFactory(date=self.today)
        with self.assertRaises(DailyAssetInfoNotFoundError):
            update_blade_server(
                {'id': 1, 'device_id': daily_asset_info.asset_info.device_id},
                self.today + datetime.timedelta(days=1),
                self.blade_server_usage_type
            )

    def test_update_blade_server_no_asset_info(self):
        daily_asset_info = DailyAssetInfoFactory.build(date=self.today)
        with self.assertRaises(AssetInfoNotFoundError):
            update_blade_server(
                {'id': 1, 'device_id': daily_asset_info.asset_info.device_id},
                self.today,
                self.blade_server_usage_type
            )

    @mock.patch('ralph_scrooge.plugins.collect.blade_server.update_blade_server')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.blade_server.get_blade_servers')  # noqa
    def test_batch_update(
        self,
        get_blade_servers_mock,
        update_blade_server_mock
    ):
        def sample_get_blade_servers():
            return SAMPLE_BLADE_SERVER

        def sample_update_blade_server_mock(data, date, usage_type):
            responses = {
                20: False,
                30: AssetInfoNotFoundError(),
                40: DailyAssetInfoNotFoundError(),
            }
            response = responses.get(data['device_id'], True)
            if isinstance(response, Exception):
                raise response
            return response

        get_blade_servers_mock.side_effect = sample_get_blade_servers
        update_blade_server_mock.side_effect = sample_update_blade_server_mock
        self.assertEquals(
            blade_server_plugin(today=self.today),
            (True, '1 new Blade Servers usages, 1 updated, 4 total')
        )

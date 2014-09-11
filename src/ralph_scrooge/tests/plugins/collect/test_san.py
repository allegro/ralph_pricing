# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.test import TestCase

from ralph_scrooge.plugins.collect.san import (
    AssetInfoNotFound,
    DailyAssetInfoNotFound,
    san as san_plugin,
    get_usage_type,
    update_san,
    update_usage,
)
from ralph_scrooge.tests.utils.factory import DailyAssetInfoFactory
from ralph_scrooge.tests.plugins.collect.samples.san import SAMPLE_SAN


class TestSanCollectPlugin(TestCase):
    def setUp(self):
        self.today = datetime.date(2014, 7, 1)
        self.san_usage_type = get_usage_type()

    def test_update_usage(self):
        daily_asset_info = DailyAssetInfoFactory(date=self.today)
        self.assertTrue(update_usage(
            daily_asset_info,
            self.today,
            1,
            self.san_usage_type,
        ))
        self.assertEquals(self.san_usage_type.dailyusage_set.count(), 1)
        daily_usage = self.san_usage_type.dailyusage_set.all()[:1].get()
        self.assertEquals(daily_usage.date, self.today)
        self.assertEquals(
            daily_usage.service_environment,
            daily_asset_info.service_environment
        )
        self.assertEquals(daily_usage.type, self.san_usage_type)
        self.assertEquals(daily_usage.value, 1)

        # update
        self.assertFalse(update_usage(
            daily_asset_info,
            self.today,
            2,
            self.san_usage_type,
        ))
        self.assertEquals(self.san_usage_type.dailyusage_set.count(), 1)
        daily_usage = self.san_usage_type.dailyusage_set.all()[:1].get()
        self.assertEquals(daily_usage.value, 2)

    @mock.patch('ralph_scrooge.plugins.collect.san.update_usage')
    def test_update_san(self, update_usage_mock):
        update_usage_mock.return_value = True
        daily_asset_info = DailyAssetInfoFactory(date=self.today)
        self.assertTrue(update_san(
            {'id': 1, 'device_id': daily_asset_info.asset_info.device_id},
            self.today,
            self.san_usage_type
        ))
        update_usage_mock.assert_called_with(
            daily_asset_info,
            self.today,
            1,
            self.san_usage_type,
        )

    def test_update_san_no_daily_asset_info(self):
        daily_asset_info = DailyAssetInfoFactory(date=self.today)
        with self.assertRaises(DailyAssetInfoNotFound):
            update_san(
                {'id': 1, 'device_id': daily_asset_info.asset_info.device_id},
                self.today + datetime.timedelta(days=1),
                self.san_usage_type
            )

    def test_update_san_no_asset_info(self):
        daily_asset_info = DailyAssetInfoFactory.build(date=self.today)
        with self.assertRaises(AssetInfoNotFound):
            update_san(
                {'id': 1, 'device_id': daily_asset_info.asset_info.device_id},
                self.today,
                self.san_usage_type
            )

    @mock.patch('ralph_scrooge.plugins.collect.san.update_san')
    @mock.patch('ralph_scrooge.plugins.collect.san.get_fc_cards')
    def test_batch_update(self, get_fc_cards_mock, update_san_mock):
        def sample_get_fc_cards():
            return SAMPLE_SAN

        def sample_update_san_mock(data, date, usage_type):
            responses = {
                20: False,
                30: AssetInfoNotFound(),
                40: DailyAssetInfoNotFound(),
            }
            response = responses.get(data['device_id'], True)
            if isinstance(response, Exception):
                raise response
            return response

        get_fc_cards_mock.side_effect = sample_get_fc_cards
        update_san_mock.side_effect = sample_update_san_mock
        self.assertEquals(
            san_plugin(today=self.today),
            (True, '1 new SAN usages, 1 updated, 4 total')
        )

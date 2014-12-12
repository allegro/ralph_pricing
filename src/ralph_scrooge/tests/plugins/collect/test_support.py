# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import patch

from django.test import TestCase

from ralph_scrooge.models import SupportCost
from ralph_scrooge.plugins.collect import support
from ralph_scrooge.tests.utils.factory import DailyAssetInfoFactory


class TestSupportPlugin(TestCase):
    def setUp(self):
        self.today = date(2014, 10, 12)
        self.daily_asset1 = DailyAssetInfoFactory()
        self.daily_asset2 = DailyAssetInfoFactory()
        self.daily_asset3 = DailyAssetInfoFactory.build()
        self.data = {
            'support_id': 1,
            'assets': [
                self.daily_asset1.asset_info.asset_id,
            ],
            'date_from': date(2014, 10, 1),
            'date_to': date(2014, 10, 30),
            'price': 30,
            'name': 'support1',
        }

    def _compare_support(self, support, pricing_object, divide_to=None):
        self.assertEquals(support.support_id, self.data['support_id'])
        self.assertEquals(support.start, self.data['date_from'])
        self.assertEquals(support.end, self.data['date_to'])
        self.assertEquals(support.remarks, self.data['name'])
        self.assertEquals(support.pricing_object.id, pricing_object.id)
        cost = self.data['price'] / (divide_to or len(self.data['assets']))
        self.assertEquals(support.cost, cost)
        self.assertEquals(support.forecast_cost, cost)

    def test_update_support(self):
        result = support.update_support(self.data)
        self.assertEquals(SupportCost.objects.count(), 1)
        self.assertEquals(result, 1)
        self._compare_support(
            SupportCost.objects.get(),
            self.daily_asset1.asset_info
        )

    def test_update_support_multiple(self):
        self.data['assets'].append(self.daily_asset2.asset_info.asset_id)
        result = support.update_support(self.data)
        self.assertEquals(result, 2)
        self.assertEquals(2, SupportCost.objects.count())

    def test_update_support_delete(self):
        SupportCost.objects.create(
            support_id=self.data['support_id'],
            pricing_object=self.daily_asset2.asset_info,
            start=self.data['date_from'],
            end=self.data['date_to'],
            cost=self.data['price'],
            forecast_cost=self.data['price'],
            remarks=self.data['name'],
        )
        self._compare_support(
            SupportCost.objects.get(),
            self.daily_asset2.asset_info
        )
        self.data['assets'].append(self.daily_asset3.asset_info.asset_id)
        result = support.update_support(self.data)
        self.assertEquals(result, 1)
        self.assertEquals(1, SupportCost.objects.count())
        self._compare_support(
            SupportCost.objects.get(),
            self.daily_asset1.asset_info
        )

    @patch('ralph_scrooge.plugins.collect.support.update_support')
    @patch('ralph_scrooge.plugins.collect.support.get_supports')
    def test_support_plugin(self, get_supports_mock, update_support_mock):
        update_support_mock.return_value = 3

        def get_supports(today):
            for i in range(2):
                yield self.data

        get_supports_mock.side_effect = get_supports

        result = support.support(self.today)
        self.assertEquals(result, (True, 'Supports: 2 total (for 6 assets)'))
        self.assertEquals(update_support_mock.call_count, 2)

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from mock import patch

from ralph_scrooge.models import SupportCost
from ralph_scrooge.plugins.collect import ralph3_support
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import DailyAssetInfoFactory
from ralph_scrooge.tests.utils.url_helpers import get_pricing_object_url


class TestRalph3SupportPlugin(ScroogeTestCase):
    def setUp(self):
        self.today = date(2017, 2, 17)
        self.daily_asset1 = DailyAssetInfoFactory()
        self.daily_asset2 = DailyAssetInfoFactory()
        self.data = {
            'id': 1,
            'base_objects': [
                get_pricing_object_url(
                    self.daily_asset1.asset_info.ralph3_asset_id
                ),
            ],
            'date_from': date(2016, 2, 1),
            'date_to': date(2017, 2, 28),
            'price': '30.0',  # price comes as string!
            'name': 'support1',
            '__str__': 'support1 (2017-02-28)'
        }

    def _compare_support(self, support, pricing_object, divide_to=None):
        self.assertEquals(support.support_id, self.data['id'])
        self.assertEquals(support.start, self.data['date_from'])
        self.assertEquals(support.end, self.data['date_to'])
        self.assertEquals(support.remarks, self.data['__str__'])
        self.assertEquals(support.pricing_object.id, pricing_object.id)
        cost = float(self.data['price']) / (
            divide_to or len(self.data['base_objects'])
        )
        self.assertEquals(support.cost, cost)
        self.assertEquals(support.forecast_cost, cost)

    def test_update_support_with_support_assigned_to_single_object_then_one_support_cost_is_created(self):  # noqa: E501
        result = ralph3_support.update_support(self.data)
        self.assertEquals(SupportCost.objects.count(), 1)
        self.assertEquals(result, 1)
        self._compare_support(
            SupportCost.objects.get(),
            self.daily_asset1.asset_info
        )

    def test_update_support_with_support_assigned_to_multiple_objects_then_two_support_costs_are_created(self):  # noqa: E501
        self.data['base_objects'].append(
            get_pricing_object_url(
                self.daily_asset2.asset_info.ralph3_asset_id
            ),
        )
        result = ralph3_support.update_support(self.data)
        self.assertEquals(result, 2)
        self.assertEquals(2, SupportCost.objects.count())

    def test_update_support_with_deleting_missing_base_object(self):
        SupportCost.objects.create(
            support_id=self.data['id'],
            pricing_object=self.daily_asset2.asset_info,
            start=self.data['date_from'],
            end=self.data['date_to'],
            cost=self.data['price'],
            forecast_cost=self.data['price'],
            remarks=self.data['__str__'],
        )
        self._compare_support(
            SupportCost.objects.get(),
            self.daily_asset2.asset_info
        )
        daily_asset3 = DailyAssetInfoFactory.build()
        self.data['base_objects'].append(
            get_pricing_object_url(
                daily_asset3.asset_info.ralph3_asset_id
            ),
        )
        result = ralph3_support.update_support(self.data)
        self.assertEquals(result, 1)
        self.assertEquals(1, SupportCost.objects.count())
        self._compare_support(
            SupportCost.objects.get(),
            self.daily_asset1.asset_info
        )

    @patch('ralph_scrooge.plugins.collect.ralph3_support.update_support')
    @patch('ralph_scrooge.plugins.collect.ralph3_support.get_from_ralph')
    def test_support_plugin(self, get_from_ralph_mock, update_support_mock):
        update_support_mock.return_value = 3

        def get_supports(endpoint, logger, query=None):
            return [self.data, self.data]

        get_from_ralph_mock.side_effect = get_supports

        result = ralph3_support.ralph3_support(today=self.today)
        self.assertEquals(
            result,
            (True, 'Support: 2 total for 6 pricing objects')
        )
        self.assertEquals(update_support_mock.call_count, 2)

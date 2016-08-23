# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock

from django.test import TestCase

from ralph_scrooge.models import BusinessLine, ProfitCenter
from ralph_scrooge.plugins.collect.ralph3_profit_center import (
    profit_center as profit_center_plugin,
    update_profit_center
)
from ralph_scrooge.tests.plugins.collect.samples.ralph3_profit_center import (
    SAMPLE_PROFIT_CENTERS,
)
from ralph_scrooge.tests.utils.factory import BusinessLineFactory


class TestProfitCenterPlugin(TestCase):
    def setUp(self):
        self.default_business_line = BusinessLine.objects.get(pk=1)
        self.business_line1 = BusinessLineFactory(
            ralph3_id=SAMPLE_PROFIT_CENTERS[0]['business_segment']['id']
        )
        self.business_line2 = BusinessLineFactory(
            ralph3_id=SAMPLE_PROFIT_CENTERS[1]['business_segment']['id']
        )

    def _compare_profit_center(self, profit_center, sample_data):
        self.assertEquals(profit_center.name, sample_data['name'])
        self.assertEquals(profit_center.ralph3_id, sample_data['id'])
        self.assertEquals(
            profit_center.description,
            sample_data['description']
        )
        self.assertEquals(
            profit_center.business_line.ralph3_id,
            sample_data['business_segment']['id']
        )

    def test_add_profit_center(self):
        sample_data = SAMPLE_PROFIT_CENTERS[0]
        self.assertTrue(update_profit_center(
            sample_data,
            self.default_business_line
        ))
        profit_center = ProfitCenter.objects.get(ralph3_id=sample_data['id'])
        self._compare_profit_center(profit_center, sample_data)

    def test_update_profit_center(self):
        sample_data = SAMPLE_PROFIT_CENTERS[0]
        self.assertTrue(update_profit_center(
            sample_data,
            self.default_business_line
        ))
        profit_center = ProfitCenter.objects.get(ralph3_id=sample_data['id'])
        self._compare_profit_center(profit_center, sample_data)

        sample_data2 = SAMPLE_PROFIT_CENTERS[1]
        sample_data2['id'] = sample_data['id']
        self.assertFalse(update_profit_center(
            sample_data2,
            self.default_business_line
        ))
        profit_center = ProfitCenter.objects.get(ralph3_id=sample_data2['id'])
        self._compare_profit_center(profit_center, sample_data2)

    @mock.patch('ralph_scrooge.plugins.collect.ralph3_profit_center.update_profit_center')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.ralph3_profit_center.get_from_ralph')  # noqa
    def test_batch_update(
        self,
        get_from_ralph_mock,
        update_profit_center_mock
    ):
        def sample_update_profit_center(data, default_business_line):
            return data['id'] % 2 == 0

        def sample_get_from_ralph(endpoint, logger):
            return SAMPLE_PROFIT_CENTERS

        update_profit_center_mock.side_effect = sample_update_profit_center
        get_from_ralph_mock.side_effect = sample_get_from_ralph
        result = profit_center_plugin()
        self.assertEquals(
            result,
            (True, '1 new profit center(s), 1 updated, 2 total')
        )
        update_profit_center_mock.call_count = 2
        update_profit_center_mock.assert_any_call(
            SAMPLE_PROFIT_CENTERS[0],
            self.default_business_line,
        )
        update_profit_center_mock.assert_any_call(
            SAMPLE_PROFIT_CENTERS[1],
            self.default_business_line,
        )

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
import mock

from django.test import TestCase

from ralph_scrooge.models import BusinessLine, ProfitCenter
from ralph_scrooge.plugins.collect.profit_center import (
    profit_center as profit_center_plugin,
    update_profit_center
)
from ralph_scrooge.tests.plugins.collect.samples.profit_center import (
    SAMPLE_PROFIT_CENTERS,
)
from ralph_scrooge.tests.utils.factory import BusinessLineFactory


class TestProfitCenterPlugin(TestCase):
    def setUp(self):
        self.today = date(2014, 7, 1)
        self.default_business_line = BusinessLine.objects.get(pk=1)
        self.business_line1 = BusinessLineFactory(
            ci_id=SAMPLE_PROFIT_CENTERS[0]['business_line']
        )
        self.business_line2 = BusinessLineFactory(
            ci_id=SAMPLE_PROFIT_CENTERS[1]['business_line']
        )

    def _compare_profit_center(self, profit_center, sample_data):
        self.assertEquals(profit_center.name, sample_data['name'])
        self.assertEquals(profit_center.ci_id, sample_data['ci_id'])
        self.assertEquals(
            profit_center.description,
            sample_data['description']
        )
        self.assertEquals(
            profit_center.business_line.ci_id,
            sample_data['business_line']
        )

    def test_add_profit_center(self):
        sample_data = SAMPLE_PROFIT_CENTERS[0]
        self.assertTrue(update_profit_center(
            sample_data,
            self.today,
            self.default_business_line
        ))
        profit_center = ProfitCenter.objects.get(ci_id=sample_data['ci_id'])
        self._compare_profit_center(profit_center, sample_data)

    def test_update_profit_center(self):
        sample_data = SAMPLE_PROFIT_CENTERS[0]
        self.assertTrue(update_profit_center(
            sample_data,
            self.today,
            self.default_business_line
        ))
        profit_center = ProfitCenter.objects.get(ci_id=sample_data['ci_id'])
        self._compare_profit_center(profit_center, sample_data)

        sample_data2 = SAMPLE_PROFIT_CENTERS[1]
        sample_data2['ci_id'] = sample_data['ci_id']
        self.assertFalse(update_profit_center(
            sample_data2,
            self.today,
            self.default_business_line
        ))
        profit_center = ProfitCenter.objects.get(ci_id=sample_data2['ci_id'])
        self._compare_profit_center(profit_center, sample_data2)

    @mock.patch('ralph_scrooge.plugins.collect.profit_center.update_profit_center')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.profit_center.get_profit_centers')  # noqa
    def test_batch_update(
        self,
        get_profit_centers_mock,
        update_profit_center_mock
    ):
        def sample_update_profit_center(data, date, default_business_line):
            return data['ci_id'] % 2 == 0

        def sample_get_profit_centers():
            for profit_center in SAMPLE_PROFIT_CENTERS:
                yield profit_center

        update_profit_center_mock.side_effect = sample_update_profit_center
        get_profit_centers_mock.side_effect = sample_get_profit_centers
        result = profit_center_plugin(today=self.today)
        self.assertEquals(
            result,
            (True, '1 new profit center(s), 1 updated, 2 total')
        )
        update_profit_center_mock.call_count = 2
        update_profit_center_mock.assert_any_call(
            SAMPLE_PROFIT_CENTERS[0],
            self.today,
            self.default_business_line,
        )
        update_profit_center_mock.assert_any_call(
            SAMPLE_PROFIT_CENTERS[1],
            self.today,
            self.default_business_line,
        )

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock

from django.test import TestCase

from ralph_scrooge.models import BusinessLine
from ralph_scrooge.plugins.collect.business_line import (
    business_line as business_line_plugin,
    update_business_line
)
from ralph_scrooge.tests.plugins.collect.samples.business_line import (
    SAMPLE_BUSINESS_LINES,
)


class TestBusinessLineCollectPlugin(TestCase):
    def _compare_business_line(self, business_line, sample_data):
        self.assertEquals(business_line.name, sample_data['name'])
        self.assertEquals(business_line.ci_id, sample_data['id'])

    def test_add_business_line(self):
        sample_data = SAMPLE_BUSINESS_LINES[0]
        self.assertTrue(update_business_line(sample_data))
        business_line = BusinessLine.objects.get(ci_id=sample_data['id'])
        self._compare_business_line(business_line, sample_data)

    def test_update_business_line(self):
        sample_data = SAMPLE_BUSINESS_LINES[0]
        self.assertTrue(update_business_line(sample_data))
        business_line = BusinessLine.objects.get(ci_id=sample_data['id'])
        self._compare_business_line(business_line, sample_data)

        sample_data2 = SAMPLE_BUSINESS_LINES[1]
        sample_data2['id'] = sample_data['id']
        self.assertFalse(update_business_line(sample_data2))
        business_line = BusinessLine.objects.get(ci_id=sample_data2['id'])
        self._compare_business_line(business_line, sample_data2)

    @mock.patch('ralph_scrooge.plugins.collect.business_line.update_business_line')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.business_line.get_from_ralph')
    def test_batch_update(
        self, get_from_ralph_mock,
        update_business_line_mock
    ):
        def sample_update_business_line(data):
            return data['id'] % 2 == 0

        def sample_get_from_ralph(endpoint, logger):
            return SAMPLE_BUSINESS_LINES

        update_business_line_mock.side_effect = sample_update_business_line
        get_from_ralph_mock.side_effect = sample_get_from_ralph
        result = business_line_plugin()
        self.assertEquals(
            result,
            (True, '1 new business line(s), 1 updated, 2 total')
        )
        update_business_line_mock.call_count = 2
        update_business_line_mock.assert_any_call(SAMPLE_BUSINESS_LINES[0])
        update_business_line_mock.assert_any_call(SAMPLE_BUSINESS_LINES[1])

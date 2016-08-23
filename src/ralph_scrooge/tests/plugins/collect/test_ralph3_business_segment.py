# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock

from django.test import TestCase

from ralph_scrooge.models import BusinessLine
from ralph_scrooge.plugins.collect.ralph3_business_segment import (
    business_segment as business_segment_plugin,
    update_business_segment
)
from ralph_scrooge.tests.plugins.collect.samples.ralph3_business_segment import (  # noqa
    SAMPLE_BUSINESS_SEGMENTS,
)


class TestBusinessLineCollectPlugin(TestCase):
    def _compare_business_line(self, business_line, sample_data):
        self.assertEquals(business_line.name, sample_data['name'])
        self.assertEquals(business_line.ralph3_id, sample_data['id'])

    def test_add_business_line(self):
        sample_data = SAMPLE_BUSINESS_SEGMENTS[0]
        self.assertTrue(update_business_segment(sample_data))
        business_line = BusinessLine.objects.get(ralph3_id=sample_data['id'])
        self._compare_business_line(business_line, sample_data)

    def test_update_business_segment(self):
        sample_data = SAMPLE_BUSINESS_SEGMENTS[0]
        self.assertTrue(update_business_segment(sample_data))
        business_line = BusinessLine.objects.get(ralph3_id=sample_data['id'])
        self._compare_business_line(business_line, sample_data)

        sample_data2 = SAMPLE_BUSINESS_SEGMENTS[1]
        sample_data2['id'] = sample_data['id']
        self.assertFalse(update_business_segment(sample_data2))
        business_line = BusinessLine.objects.get(ralph3_id=sample_data2['id'])
        self._compare_business_line(business_line, sample_data2)

    @mock.patch('ralph_scrooge.plugins.collect.ralph3_business_segment.update_business_segment')  # noqa
    @mock.patch('ralph_scrooge.plugins.collect.ralph3_business_segment.get_from_ralph')  # noqa
    def test_batch_update(
        self, get_from_ralph_mock,
        update_business_segment_mock
    ):
        def sample_update_business_segment(data):
            return data['id'] % 2 == 0

        def sample_get_from_ralph(endpoint, logger):
            return SAMPLE_BUSINESS_SEGMENTS

        update_business_segment_mock.side_effect = sample_update_business_segment  # noqa
        get_from_ralph_mock.side_effect = sample_get_from_ralph
        result = business_segment_plugin()
        self.assertEquals(
            result,
            (True, '1 new business segment(s), 1 updated, 2 total')
        )
        update_business_segment_mock.call_count = 2
        update_business_segment_mock.assert_any_call(
            SAMPLE_BUSINESS_SEGMENTS[0]
        )
        update_business_segment_mock.assert_any_call(
            SAMPLE_BUSINESS_SEGMENTS[1]
        )

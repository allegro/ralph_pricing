# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from django.test import TestCase

from ralph_scrooge.utils import common


class TestRangesOverlap(TestCase):
    def test_overlap_on_start(self):
        self.assertTrue(common.ranges_overlap(10, 20, 15, 25))

    def test_overlap_on_end(self):
        self.assertTrue(common.ranges_overlap(20, 30, 15, 25))

    def test_overlap_inside(self):
        self.assertTrue(common.ranges_overlap(10, 30, 15, 25))

    def test_overlap_outside(self):
        self.assertTrue(common.ranges_overlap(15, 25, 10, 30))

    def test_not_overlapping(self):
        self.assertFalse(common.ranges_overlap(10, 15, 16, 30))
        self.assertFalse(common.ranges_overlap(15, 30, 10, 14))

    def test_sum_of_intervals(self):
        intervals = [(1, 5), (4, 10), (7, 13), (15, 20), (21, 30)]
        result = common.sum_of_intervals(intervals)
        self.assertEquals([(1, 13), (15, 20), (21, 30)], result)

    def test_sum_of_dates_intervals(self):
        intervals = [
            (date(2013, 10, 10), date(2013, 10, 15)),
            (date(2013, 10, 10), date(2013, 10, 15)),
            (date(2013, 10, 12), date(2013, 10, 14)),
            (date(2013, 10, 14), date(2013, 10, 19)),
            (date(2013, 10, 21), date(2013, 10, 28)),
        ]
        result = common.sum_of_intervals(intervals)
        self.assertEquals(
            [
                (date(2013, 10, 10), date(2013, 10, 19)),
                (date(2013, 10, 21), date(2013, 10, 28)),
            ],
            result
        )

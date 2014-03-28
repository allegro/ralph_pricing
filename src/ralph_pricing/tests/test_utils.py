# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase

from ralph_pricing import utils


class TestRangesOverlap(TestCase):
    def test_overlap_on_start(self):
        self.assertTrue(utils.ranges_overlap(10, 20, 15, 25))

    def test_overlap_on_end(self):
        self.assertTrue(utils.ranges_overlap(20, 30, 15, 25))

    def test_overlap_inside(self):
        self.assertTrue(utils.ranges_overlap(10, 30, 15, 25))

    def test_overlap_outside(self):
        self.assertTrue(utils.ranges_overlap(15, 25, 10, 30))

    def test_not_overlapping(self):
        self.assertFalse(utils.ranges_overlap(10, 15, 16, 30))
        self.assertFalse(utils.ranges_overlap(15, 30, 10, 14))

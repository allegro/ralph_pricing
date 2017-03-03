# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date

from ralph_scrooge.models import ServiceUsageTypes
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    DailyUsageFactory,
    PricingServiceFactory,
    ServiceEnvironmentFactory,
    UsageTypeFactory
)
from ralph_scrooge.utils import common, cycle_detector


class TestRangesOverlap(ScroogeTestCase):
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


class TestCyclesDetector(ScroogeTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCyclesDetector, cls).setUpClass()
        cls.today = date(2017, 3, 3)
        cls.se1, cls.se2, cls.se3, cls.se4 = ServiceEnvironmentFactory.create_batch(4)

        cls.ps1 = PricingServiceFactory()
        cls.ps1.services.add(cls.se1.service)
        cls.usage_type1 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=cls.usage_type1,
            pricing_service=cls.ps1,
            start=date.min,
            end=date.max,
        )
        cls.usage_type2 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=cls.usage_type2,
            pricing_service=cls.ps1,
            start=date.min,
            end=date.max,
        )

        cls.ps2 = PricingServiceFactory()
        cls.ps2.services.add(cls.se2.service)
        cls.usage_type3 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=cls.usage_type3,
            pricing_service=cls.ps2,
            start=date.min,
            end=date.max,
        )

        cls.ps3 = PricingServiceFactory()
        cls.ps3.services.add(cls.se3.service)
        cls.usage_type4 = UsageTypeFactory()
        ServiceUsageTypes.objects.create(
            usage_type=cls.usage_type4,
            pricing_service=cls.ps3,
            start=date.min,
            end=date.max,
        )

    def setUp(self):
        DailyUsageFactory(
            type=self.usage_type1,
            service_environment=self.se2,
            date=self.today
        )
        DailyUsageFactory(
            type=self.usage_type3,
            service_environment=self.se3,
            date=self.today
        )

    def _make_cycle(self):
        DailyUsageFactory(
            type=self.usage_type4,
            service_environment=self.se1,
            date=self.today
        )

    def test_get_pricing_services_graph_when_graph_is_without_cycle(self):
        graph = cycle_detector._get_pricing_services_graph(self.today)
        self.assertEqual(graph, {
            self.ps1: [self.ps2],
            self.ps2: [self.ps3],
        })

    def test_get_pricing_services_graph_when_graph_is_with_cycle(self):
        self._make_cycle()
        graph = cycle_detector._get_pricing_services_graph(self.today)
        self.assertEqual(graph, {
            self.ps1: [self.ps2],
            self.ps2: [self.ps3],
            self.ps3: [self.ps1],
        })

    def test_detect_cycle_when_there_is_no_cycle(self):
        cycles = cycle_detector.detect_cycles(self.today)
        self.assertEqual(cycles, [])

    def test_detect_cycle_when_there_is_cycle(self):
        self._make_cycle()
        graph = cycle_detector._get_pricing_services_graph(self.today)
        cycles = cycle_detector._detect_cycles(self.ps1, graph, set(), [])
        self.assertEqual(cycles, [[self.ps1, self.ps2, self.ps3, self.ps1]])

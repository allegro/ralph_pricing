# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date, timedelta
from dateutil import rrule
import mock

from django.test import TestCase

from ralph_scrooge.plugins.cost.collector import Collector
from ralph_scrooge.tests.utils.factory import (
    CostDateStatusFactory,
    ServiceEnvironmentFactory,
)


class TestCollector(TestCase):
    def setUp(self):
        self.today = date(2013, 10, 11)
        self.checkpoint = date(2013, 10, 15)
        self.start = date(2013, 10, 1)
        self.end = date(2013, 10, 30)
        self.service_environments = ServiceEnvironmentFactory.create_batch(2)
        self.collector = Collector()

        self.dates1 = self._dates_between(self.start, self.checkpoint)
        self.dates2 = self._dates_between(
            self.checkpoint + timedelta(days=1),
            self.end
        )
        self.dates = self._dates_between(self.start, self.end)

    def _dates_between(self, start, end):
        return [d.date() for d in rrule.rrule(
            rrule.DAILY,
            dtstart=start,
            until=end
        )]

    def test_get_dates_force_recalculation(self):
        dates = self.collector._get_dates(self.start, self.end, True, True)
        self.assertEquals(dates, self.dates)

    def test_get_dates_forecast(self):
        for days, calculated in [(self.dates1, True), (self.dates2, False)]:
            for day in days:
                CostDateStatusFactory(date=day, forecast_calculated=calculated)
        dates = self.collector._get_dates(self.start, self.end, True, False)
        self.assertEquals(dates, self.dates2)

    def test_get_dates(self):
        for days, calculated in [(self.dates1, True), (self.dates2, False)]:
            for day in days:
                CostDateStatusFactory(date=day, calculated=calculated)
        dates = self.collector._get_dates(self.start, self.end, False, False)
        self.assertEquals(dates, self.dates2)

    def test_get_services_environments(self):
        se = self.collector._get_services_environments()
        self.assertEquals(list(se), [
            self.service_environments[0],
            self.service_environments[1],
        ])

    @mock.patch('ralph_scrooge.plugins.cost.collector.Collector.process')
    @mock.patch('ralph_scrooge.plugins.cost.collector.Collector._get_dates')
    @mock.patch('ralph_scrooge.plugins.cost.collector.Collector._get_services_environments')  # noqa
    def test_process_period(self, get_se_mock, get_dates_mock, process_mock):
        get_dates_mock.return_value = self.dates1
        process_mock.return_value = None
        get_se_mock.return_value = self.service_environments
        for day, success in self.collector.process_period(
            self.start,
            self.end,
            True,
            False,
            a=1,
            service_environments=self.service_environments,
        ):
            pass
        calls = []
        for day in self.dates1:
            calls.append(mock.call(
                day,
                service_environments=self.service_environments,
                forecast=True,
                a=1,
            ))
        process_mock.assert_has_calls(calls)

    # TODO: add more unit tests

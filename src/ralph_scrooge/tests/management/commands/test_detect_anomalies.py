# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.conf import settings

from ralph_scrooge.management.commands.detect_usage_anomalies import (
    _get_max_expected_date,
    UnknownUsageTypeUploadFreqError,
)
from ralph_scrooge.models import UsageTypeUploadFreq
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import UsageTypeFactory


class TestGetMaxExpectedDate(ScroogeTestCase):

    def setUp(self):
        settings.USAGE_TYPE_UPLOAD_FREQ_MARGINS = {
            'daily': 1,
            'weekly': 2,
            'monthly': 3,
        }
        self.freq_daily = UsageTypeUploadFreq.from_name('daily')
        self.freq_weekly = UsageTypeUploadFreq.from_name('weekly')
        self.freq_monthly = UsageTypeUploadFreq.from_name('monthly')

    @mock.patch('ralph_scrooge.models.usage.UsageTypeUploadFreq.from_id')
    def test_for_error_when_unknown_upload_freq_given(self, freq_from_id):
        # 'unknown' i.e. present in UsageTypeUploadFreq, but not known/handled
        # in _get_max_expected_date.
        fake_upload_freq = type(
            str('UsageTypeUploadFreq'),
            (object,),
            {'id': 999, 'name': 'fake_freq', 'margin': 1},
        )
        freq_from_id.return_value = fake_upload_freq
        ut = UsageTypeFactory(upload_freq=fake_upload_freq.id)
        date = datetime.date(2016, 11, 18)
        self.assertRaises(
            UnknownUsageTypeUploadFreqError, _get_max_expected_date, ut, date
        )

    def test_for_success_when_daily_freq_given(self):
        ut = UsageTypeFactory(upload_freq=self.freq_daily.id)

        date = datetime.date(2016, 11, 18)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 11, 17))

        date = datetime.date(2016, 1, 1)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2015, 12, 31))

    def test_for_success_when_weekly_freq_given(self):
        ut = UsageTypeFactory(upload_freq=self.freq_weekly.id)

        date = datetime.date(2016, 11, 15)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 11, 13))
        self.assertEquals(max_date.isoweekday(), 7)

        date = datetime.date(2016, 11, 14)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 11, 6))
        self.assertEquals(max_date.isoweekday(), 7)

    def test_for_success_when_montlhy_freq_given(self):
        ut = UsageTypeFactory(upload_freq=self.freq_monthly.id)

        date = datetime.date(2016, 11, 1)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 9, 30))

        date = datetime.date(2016, 11, 2)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 9, 30))

        date = datetime.date(2016, 11, 3)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 10, 31))

        date = datetime.date(2016, 11, 4)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 10, 31))

        date = datetime.date(2016, 11, 30)
        max_date = _get_max_expected_date(ut, date)
        self.assertEquals(max_date, datetime.date(2016, 10, 31))

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.conf import settings

from ralph_scrooge.management.commands.detect_usage_anomalies import (
    _detect_missing_values,
    _get_max_expected_date,
    UnknownUsageTypeUploadFreqError,
)
from ralph_scrooge.models import (
    PricingServicePlugin,
    ServiceUsageTypes,
    UsageTypeUploadFreq,
)
from ralph_scrooge.tests import ScroogeTestCase
from ralph_scrooge.tests.utils.factory import (
    PricingServiceFactory,
    UsageTypeFactory,
)


FIXED_PRICE_PLUGIN = PricingServicePlugin.pricing_service_fixed_price_plugin


class TestDetectMissingValues(ScroogeTestCase):

    def test_if_dates_not_present_in_pricing_services_will_be_ignored_even_if_there_are_missing_values(self):  # noqa: E501
        ut = UsageTypeFactory(upload_freq=UsageTypeUploadFreq.daily.id)
        ps1 = PricingServiceFactory(plugin_type=FIXED_PRICE_PLUGIN)
        ps2 = PricingServiceFactory(plugin_type=FIXED_PRICE_PLUGIN)

        # There will be a "hole" from 2016-12-16 to 2016-12-24 (i.e. 9 days)
        ServiceUsageTypes.objects.create(
            usage_type=ut,
            pricing_service=ps1,
            start=datetime.datetime(2016, 12, 1),
            end=datetime.datetime(2016, 12, 15)
        )
        ServiceUsageTypes.objects.create(
            usage_type=ut,
            pricing_service=ps2,
            start=datetime.datetime(2016, 12, 25),
            end=datetime.datetime(2017, 01, 10)
        )

        usage_values = {ut: {}}  # no usages uploaded at all
        end_date = datetime.datetime(2017, 1, 9).date()
        missing_values = _detect_missing_values(usage_values, end_date)

        # 30 days taken into account minus 9 days ("hole") == 21 expected here.
        self.assertEqual(len(missing_values.values()[0]), 21)


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import mock

from django.conf import settings
from django.test import TestCase

from ralph_pricing.models import DailyDevice, Device, DailyUsage, Venture
from ralph_pricing.plugins.collects.splunk import (
    splunk as splunk_runner,
)
from ralph_pricing.tests.collect_plugins.samples.splunk import (
    hosts_usages_data
)


class MockSplunk(object):
    """ Simple mock for Splunk API library """
    def __init__(self, *args, **kwargs):
        pass

    @property
    def progress(self, *args, **kwargs):
        return 100.1

    @property
    def results(self, *args, **kwargs):
        return hosts_usages_data

    def start(self, *args, **kwargs):
        pass


def mock_get_device_by_name(host):
    for hosts_data in hosts_usages_data:
        if hosts_data['host'] == host:
            return {
                'device_id': hosts_data['device_id'],
                'venture_id': hosts_data['venture_id'],
            }
    return {}


class TestSplunkPluginTest(TestCase):
    """ Splunk costs Test Case """
    SPLUNK_PLUGIN_PATH = 'ralph_pricing.plugins.collects.splunk.Splunk'

    def setUp(self):
        self.splunk_venture = Venture(
            name='Splunk unknown usage',
            venture_id=666,
            symbol='splunk_unknown_usage',
        )
        self.splunk_venture.save()
        venture1 = Venture(name='venture1', venture_id=111, symbol='venture1')
        venture1.save()
        venture2 = Venture(name='venture2', venture_id=222, symbol='venture2')
        venture2.save()

        self.device1 = Device(name='test_host1', device_id=1)
        self.device1.save()
        self.device2 = Device(name='test_host2', device_id=2)
        self.device2.save()

        daily_device1 = DailyDevice(
            date=datetime.datetime.today(),
            name='test_host1',
            pricing_venture=venture1,
            pricing_device=self.device1,
        )
        daily_device1.save()
        daily_device2 = DailyDevice(
            date=datetime.datetime.today(),
            name='test_host2',
            pricing_venture=venture2,
            pricing_device=self.device2,
        )
        daily_device2.save()

    def test_set_usages(self):
        """ OpenStack usages Test Case """
        # fake setting need to run plugin
        settings.SPLUNK_HOST = 'test'
        settings.SPLUNK_USER = 'test'
        settings.SPLUNK_PASSWORD = 'test'
        splunk_runner.func_globals['get_device_by_name'] =\
            mock_get_device_by_name
        with mock.patch(self.SPLUNK_PLUGIN_PATH) as Splunk:
            Splunk.side_effect = MockSplunk
            splunk_runner(today=datetime.date.today())
            usage_device1 = DailyUsage.objects.get(pricing_device=self.device1)
            usage_device2 = DailyUsage.objects.get(pricing_device=self.device2)
            usage_splunk_venture = DailyUsage.objects.get(
                pricing_venture=self.splunk_venture,
            )
            self.assertEqual(usage_device1.value, 10318.234132)
            self.assertEqual(usage_device2.value, 1326.640829)
            self.assertEqual(usage_splunk_venture.value, 1048.363416)

    def test_fail_plugin(self):
            """ Testing not configured plugin """
            with mock.patch(self.SPLUNK_PLUGIN_PATH) as Splunk:
                Splunk.side_effect = MockSplunk
                status, message, arg = splunk_runner(
                    today=datetime.datetime.today(),
                )
                self.assertFalse(status)

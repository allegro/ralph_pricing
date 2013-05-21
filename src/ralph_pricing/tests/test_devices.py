# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing.models import Device, Venture, DailyDevice
from ralph_pricing.views.devices import Devices


class TestDevices(TestCase):
    fixtures = ['tests.yaml']

    def setUp(self):
        self.devices = Device.objects.all()
        self.ventures = Venture.objects.all()
        self.daily_host1 = DailyDevice.objects.filter(pricing_device=1)
        self.daily_host2 = DailyDevice.objects.filter(pricing_device=2)
        self.daily_host3 = DailyDevice.objects.filter(pricing_device=3)
        self.daily_host4 = DailyDevice.objects.filter(pricing_device=4)

    def test_fixtures(self):
        self.assertEqual(len(self.devices), 4)
        self.assertEqual(len(self.ventures), 2)
        self.assertEqual(len(self.daily_host1), 4)
        self.assertEqual(len(self.daily_host2), 4)
        self.assertEqual(len(self.daily_host3), 4)
        self.assertEqual(len(self.daily_host4), 4)

    def test_device(self):
        start_date = '2013-01-01'
        end_date = '2013-01-04'
        venture = self.ventures.get(name='Infra')
        devices_list = [
            item for item in Devices.get_data(start_date, end_date, venture)
        ]
        self.assertEqual(len(devices_list), 4)

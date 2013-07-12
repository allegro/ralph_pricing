# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from decimal import Decimal
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

    def get_data(self, start_date, end_date, venture):
        for percent, devices_list in Devices.get_data(
            start_date,
            end_date,
            venture,
        ):
            pass
        return devices_list

    def test_device(self):
        venture = self.ventures.get(name='Infra')
        start_date = datetime.date(2013, 01, 01)
        end_date = datetime.date(2013, 01, 04)
        devices_list = self.get_data(start_date, end_date, venture)
        self.assertEqual(len(devices_list), 12)
        data = [
            [
                u'ExtraCost1 (Extra Cost)',
                u'',
                u'',
                u'2013-01-01 - 2013-01-04',
                u'',
                u'100.00 PLN',
                u'',
                u'',
                u'',
                u'',
            ],
            [
                u'ExtraCost2 (Extra Cost)',
                u'',
                u'',
                u'2013-01-01 - 2013-01-04',
                u'',
                u'200.00 PLN',
                u'',
                u'',
                u'',
                u'',
            ],
            [
                u'',
                u'',
                u'DiskShare',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                100.0,
            ],
            [
                u'',
                u'',
                u'DiskShare2',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                400.0,
            ],
            [
                u'host01.dc1',
                u'',
                u'',
                u'1234-1234-1234-1234',
                u'2345-2345-2345-2345',
                u'2013-01-01: False',
                u'275.00 PLN',
                u'3.72 PLN',
                u'',
            ],
            [
                u'',
                u'hdd-0001',
                u'',
                u'',
                u'',
                u'',
                '175.00 PLN',
                u'2.37 PLN',
                u'',
            ],
            [
                u'',
                u'ram-0001',
                u'',
                u'',
                u'',
                u'',
                u'100.00 PLN',
                u'1.35 PLN',
                u'',
            ],
            [
                u'',
                u'',
                u'DiskShare',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                350.0,
            ],
            [
                u'host02.dc1',
                u'',
                u'',
                u'2345-2345-2345-2345',
                u'3456-3456-3456-3456',
                u'2013-01-01: False',
                u'175.00 PLN',
                u'0.00 PLN',
                u'',
            ],
            [
                u'',
                u'',
                u'DiskShare2',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                975.0,
            ],
            [
                u'host03.dc1',
                u'',
                u'',
                u'3456-3456-3456-3456',
                u'4567-4567-4567-4567',
                u'2013-01-01: False 2013-01-03: True 2013-01-04: False',
                u'187.50 PLN',
                u'0.00 PLN',
                u'',
            ],
            [
                u'host04.dc1',
                u'',
                u'',
                u'4567-4567-4567-4567',
                u'5678-5678-5678-5678',
                u'2013-01-01: False',
                u'50.00 PLN',
                u'0.00 PLN',
                u''
            ],
        ]

        i = 0
        for device in devices_list:
            self.assertEqual(devices_list[i], data[i])
            i += 1
        start_date = datetime.date(2013, 01, 02)
        end_date = datetime.date(2013, 01, 04)
        devices_list = self.get_data(start_date, end_date, venture)
        self.assertEqual(len(devices_list), 6)
        data = [
            [
                u'',
                u'',
                u'DiskShare',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                100.0,
            ],
            [
                u'',
                u'',
                u'DiskShare2',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                300.0,
            ],
            [
                u'host02.dc1',
                u'',
                u'',
                u'2345-2345-2345-2345',
                u'3456-3456-3456-3456',
                u'2013-01-02: False',
                u'200.00 PLN',
                u'0.00 PLN',
                u'',
            ],
            [
                u'',
                u'',
                u'DiskShare2',
                u'',
                u'',
                u'',
                u'',
                u'0.00 PLN',
                575.0,
            ],
            [
                u'host03.dc1',
                u'',
                u'',
                u'3456-3456-3456-3456',
                u'4567-4567-4567-4567',
                u'2013-01-02: False 2013-01-03: True 2013-01-04: False',
                u'166.67 PLN',
                u'0.00 PLN',
                u'',
            ],
            [
                u'host04.dc1',
                u'',
                u'',
                u'4567-4567-4567-4567',
                u'5678-5678-5678-5678',
                u'2013-01-02: False',
                u'50.00 PLN',
                u'0.00 PLN',
                u'',
            ],
        ]
        i = 0
        for device in devices_list:
            self.assertEqual(devices_list[i], data[i])
            i += 1

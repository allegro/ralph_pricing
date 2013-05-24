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
        self.assertEqual(len(devices_list), 4)
        self.assertEqual(
            devices_list,
            [
                [
                    u'host01.dc1',
                    u'1234-1234-1234-1234',
                    u'2345-2345-2345-2345',
                    u'2013-01-01: False',
                    u'50.00 PLN',
                    [
                        {
                            u'price': Decimal('175.000000'),
                            u'name': u'hdd-0001',
                        },
                        {
                            u'price': Decimal('100.000000'),
                            u'name': u'ram-0001',
                        },
                    ],
                ],
                [
                    u'host02.dc1',
                    u'2345-2345-2345-2345',
                    u'3456-3456-3456-3456',
                    u'2013-01-01: False',
                    u'175.00 PLN',
                    [],
                ],
                [
                    u'host03.dc1',
                    u'3456-3456-3456-3456',
                    u'4567-4567-4567-4567',
                    u'2013-01-01: False 2013-01-03: True 2013-01-04: False',
                    u'250.00 PLN',
                    [],
                ],
                [
                    u'host04.dc1',
                    u'4567-4567-4567-4567',
                    u'5678-5678-5678-5678',
                    u'2013-01-01: False',
                    u'50.00 PLN',
                    [],
                ],
            ]
        )

        start_date = datetime.date(2013, 01, 02)
        end_date = datetime.date(2013, 01, 04)
        devices_list = self.get_data(start_date, end_date, venture)
        self.assertEqual(len(devices_list), 3)
        self.assertEqual(
            devices_list,
            [
                [
                    u'host02.dc1',
                    u'2345-2345-2345-2345',
                    u'3456-3456-3456-3456',
                    u'2013-01-02: False',
                    u'200.00 PLN',
                    [],
                ],
                [
                    u'host03.dc1',
                    u'3456-3456-3456-3456',
                    u'4567-4567-4567-4567',
                    u'2013-01-02: False 2013-01-03: True 2013-01-04: False',
                    u'250.00 PLN',
                    [],
                ],
                [
                    u'host04.dc1',
                    u'4567-4567-4567-4567',
                    u'5678-5678-5678-5678',
                    u'2013-01-02: False',
                    u'50.00 PLN',
                    [],
                ],
            ]
        )

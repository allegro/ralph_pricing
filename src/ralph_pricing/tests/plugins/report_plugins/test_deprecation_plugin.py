# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from dateutil import rrule
from decimal import Decimal as D

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ralph_pricing import models
from ralph_pricing.tests import utils
from ralph_pricing.plugins.reports.deprecation import Deprecation


class TestDeprecationReportPlugin(TestCase):
    def setUp(self):
        # ventures
        self.venture1 = utils.get_or_create_venture()
        self.venture2 = utils.get_or_create_venture()
        self.venture3 = utils.get_or_create_venture()
        self.ventures_subset = [self.venture1, self.venture2]
        self.ventures = models.Venture.objects.all()
        self.ventures_devices = {}

        # devices
        # add j*5 devices for each venture
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        for j, venture in enumerate(self.ventures, start=1):
            self.ventures_devices[venture.id] = []
            for k in range(j * 5):
                # add device
                device = utils.get_or_create_device()
                self.ventures_devices[venture.id].append(device.id)
                for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                    utils.get_or_create_dailydevice(
                        date=day,
                        venture=venture,
                        device=device,
                        name=device.name,
                        price=1460*j,
                        deprecation_rate=25,
                        is_deprecated=False,
                    )

    def test_dailyusages(self):
        device = utils.get_or_create_device()
        utils.get_or_create_dailydevice(
            date=datetime.date(2013, 10, 12),
            venture=self.venture1,
            device=device,
            name=device.name,
            price=100,
            deprecation_rate=0.25,
            is_deprecated=False,
        )
        result = Deprecation(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 13),
            ventures=self.ventures_subset,
            type='dailyusages',
        )
        self.assertEquals(result, {
            datetime.date(2013, 10, 10): {
                self.venture1.id: 5,
                self.venture2.id: 10,
            },
            datetime.date(2013, 10, 11): {
                self.venture1.id: 5,
                self.venture2.id: 10,
            },
            datetime.date(2013, 10, 12): {
                self.venture1.id: 6,  # additional device!
                self.venture2.id: 10,
            },
            datetime.date(2013, 10, 13): {
                self.venture1.id: 5,
                self.venture2.id: 10,
            },
        })

    def test_costs(self):
        result = Deprecation(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=self.ventures_subset,
        )
        # dailycost of asset for venture 1 is 1460*25/36500 = 1
        # dailycost of asset for venture 2 is 2920*25/36500 = 2
        self.assertEquals(result, {
            self.venture1.id: {
                'assets_cost': D('55'),  # 1 * 5 (devices) * 11 (days)
                'assets_count': 5.0
            },
            self.venture2.id: {
                'assets_cost': D('220'),  # 2 * 10 (devices) * 11 (days)
                'assets_count': 10.0
            }
        })

    def test_costs_per_device(self):
        result = Deprecation(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=[self.venture1],
            type='costs_per_device',
        )
        expected = dict((v, {
            'assets_cost': D('11'),
            'assets_count': 1.0,
            'deprecation_rate': D('25'),
            'is_deprecated': _('No')
        }) for v in self.ventures_devices[self.venture1.id])
        self.assertEquals(result, expected)

    def test_costs_per_device_partially_deprecated(self):
        venture = utils.get_or_create_venture()
        device = utils.get_or_create_device()
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 10),
            device,
            venture,
            price=1460,
            deprecation_rate=25,
            is_deprecated=False,
        )
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 11),
            device,
            venture,
            price=1460,
            deprecation_rate=25,
            is_deprecated=True,
        )
        result = Deprecation(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 13),
            ventures=[venture],
            type='costs_per_device',
        )
        self.assertEquals(result, {
            device.id: {
                'assets_cost': D('1'),
                'assets_count': 0.5,
                'deprecation_rate': D('25'),
                'is_deprecated': _('Partially')
            }
        })

    def test_costs_per_device_deprecated(self):
        venture = utils.get_or_create_venture()
        device = utils.get_or_create_device()
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 10),
            device,
            venture,
            price=1460,
            deprecation_rate=25,
            is_deprecated=True,
        )
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 11),
            device,
            venture,
            price=1460,
            deprecation_rate=25,
            is_deprecated=True,
        )
        result = Deprecation(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 13),
            ventures=[venture],
            type='costs_per_device',
        )
        self.assertEquals(result, {
            device.id: {
                'assets_cost': D('0'),
                'assets_count': 0.5,
                'deprecation_rate': D('25'),
                'is_deprecated': _('Yes')
            }
        })

    def test_total_cost(self):
        result = Deprecation(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 25),
            ventures=self.ventures_subset,
            type='total_cost',
        )
        # venture1: 13 (days) * 1 (daily cost) * 5 (devices) = 65
        # venture2: 13 (days) * 2 (daily cost) * 10 (devices) 260
        self.assertEquals(result, D('325'))

    def test_get_asset_count_and_cost(self):
        result = Deprecation.get_assets_count_and_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=self.ventures_subset,
        )
        self.assertEquals(list(result), [
            {
                'assets_cost': D('55'),  # 1 * 5 (devices) * 11 (days)
                'assets_count': 55.0,  # 5 (devices) * 11 (days)
                'pricing_venture': self.venture1.id,
            },
            {
                'assets_cost': D('220'),  # 2 * 10 (devices) * 11 (days)
                'assets_count': 110.0,  # 10 (devices) * 11 (days)
                'pricing_venture': self.venture2.id,
            }
        ])

    def test_get_asset_count_and_cost_group_by_device(self):
        venture = utils.get_or_create_venture()
        device1 = utils.get_or_create_device()
        device2 = utils.get_or_create_device()
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 10),
            device1,
            venture,
            price=1460,
            deprecation_rate=25,
            is_deprecated=False,
        )
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 11),
            device2,
            venture,
            price=1460,
            deprecation_rate=25,
            is_deprecated=False,
        )
        utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 12),
            device2,
            self.venture1,
            price=1460,
            deprecation_rate=25,
            is_deprecated=False,
        )
        result = Deprecation.get_assets_count_and_cost(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 20),
            ventures=[venture],
            group_by='pricing_device',
        )
        self.assertEquals(list(result), [
            {
                'assets_cost': D('1'),
                'assets_count': 1.0,
                'pricing_device': device1.id,
            },
            {
                'assets_cost': D('1'),
                'assets_count': 1.0,
                'pricing_device': device2.id,
            }
        ])

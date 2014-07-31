# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from dateutil import rrule

from django.test import TestCase

from ralph_pricing import models
from ralph_pricing.tests import utils
from ralph_pricing.plugins.reports.information import Information


class TestInformationPlugin(TestCase):
    def setUp(self):
        # ventures
        self.venture1 = utils.get_or_create_venture(
            is_active=True,
            business_segment='bs1',
            department='d1',
            profit_center='p1',
        )
        self.venture2 = utils.get_or_create_venture(
            is_active=True,
            business_segment='bs1',
            department='d1',
            profit_center='p1',
        )
        self.venture3 = utils.get_or_create_venture(
            is_active=True,
            business_segment='bs1',
            department='d1',
            profit_center='p1',
        )
        self.ventures_subset = [self.venture1, self.venture2]
        self.ventures = models.Venture.objects.all()

    def test_costs(self):
        result = Information(
            ventures=self.ventures_subset,
        )
        self.assertEquals(result, {
            self.venture1.id: {
                'business_segment': 'bs1',
                'department': 'd1',
                'profit_center': 'p1',
                'venture': self.venture1.name,
                'venture_id': self.venture1.venture_id,
            },
            self.venture2.id: {
                'business_segment': 'bs1',
                'department': 'd1',
                'profit_center': 'p1',
                'venture': self.venture2.name,
                'venture_id': self.venture2.venture_id,
            }
        })

    def test_costs_per_device(self):
        device1 = utils.get_or_create_device(
            asset_id=1234,
            barcode='12345',
            sn='1111-1111-1111',
        )
        device2 = utils.get_or_create_device(
            asset_id=1235,
            barcode='12346',
            sn='1111-1111-1112',
        )
        start = datetime.date(2013, 10, 8)
        end = datetime.date(2013, 10, 22)
        for i, device in enumerate([device1, device2]):
            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                utils.get_or_create_dailydevice(
                    date=day,
                    name='Device{0}'.format(i),
                    price=100 * i,
                    deprecation_rate=0.25,
                    is_deprecated=False,
                    venture=self.venture1,
                    device=device,
                )

        result = Information(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 25),
            ventures=[self.venture1],
            type='costs_per_device',
        )
        self.assertEquals(result, {
            device1.id: {
                'asset_id': 1234,
                'barcode': '12345',
                'id': device1.id,
                'name': 'Default1234',
                'sn': '1111-1111-1111'
            },
            device2.id: {
                'asset_id': 1235,
                'barcode': '12346',
                'id': device2.id,
                'name': 'Default1235',
                'sn': '1111-1111-1112'
            }
        })

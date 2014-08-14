# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from dateutil import rrule

from django.test import TestCase

from ralph_scrooge.tests import utils
from ralph_scrooge.plugins.reports.information import Information


class TestInformationPlugin(TestCase):
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

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from ralph_pricing.tests import utils
from ralph_pricing.views.ventures_changes import VenturesChanges


class TestReportVenturesChanges(TestCase):
    def setUp(self):
        self.venture1 = utils.get_or_create_venture()
        self.venture2 = utils.get_or_create_venture()
        self.venture3 = utils.get_or_create_venture(parent=self.venture1)

        self.device1 = utils.get_or_create_device(
            device_id=11,
            sn='1111-1111-1111',
            barcode='12345',
        )
        self.device2 = utils.get_or_create_device(
            device_id=12,
            sn='1111-1111-1112',
            barcode='12346',
        )

        self.dailydevice1_1 = utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 10),
            self.device1,
            self.venture1,
            name=self.device1.name,
        )
        self.dailydevice1_2 = utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 11),
            self.device1,
            self.venture2,
            name=self.device1.name,
        )
        self.dailydevice2_1 = utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 10),
            self.device2,
            self.venture2,
            name=self.device2.name,
        )
        self.dailydevice2_1 = utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 11),
            self.device2,
            self.venture1,
            name=self.device2.name,
        )
        self.dailydevice3_1 = utils.get_or_create_dailydevice(
            datetime.date(2013, 10, 12),
            self.device1,
            self.venture3,
            name=self.device1.name,
        )

    def test_report_without_subtrees(self):
        for percent, result in VenturesChanges.get_data(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 12),
            venture=self.venture1,
            use_subventures=False,
        ):
            pass
        change_date = datetime.date(2013, 10, 11)
        self.assertEquals(result, [
            [
                '1111-1111-1111',
                '12345',
                self.device1.name,
                change_date,
                self.venture1.name,
                self.venture2.name,
            ],
            [
                '1111-1111-1112',
                '12346',
                self.device2.name,
                change_date,
                self.venture2.name,
                self.venture1.name,
            ],
        ])

    def test_report_with_subtrees(self):
        for percent, result in VenturesChanges.get_data(
            start=datetime.date(2013, 10, 12),
            end=datetime.date(2013, 10, 12),
            venture=self.venture1,
            use_subventures=True
        ):
            pass
        self.assertEquals(result, [
            [
                '1111-1111-1111',
                '12345',
                self.device1.name,
                datetime.date(2013, 10, 12),
                self.venture2.name,
                self.venture3.name,
            ],
        ])

    def test_report_without_venture(self):
        for percent, result in VenturesChanges.get_data(
            start=datetime.date(2013, 10, 10),
            end=datetime.date(2013, 10, 12),
        ):
            pass
        self.assertEquals(result, [
            [
                '1111-1111-1111',
                '12345',
                self.device1.name,
                datetime.date(2013, 10, 11),
                self.venture1.name,
                self.venture2.name,
            ],
            [
                '1111-1111-1112',
                '12346',
                self.device2.name,
                datetime.date(2013, 10, 11),
                self.venture2.name,
                self.venture1.name,
            ],
            [
                '1111-1111-1111',
                '12345',
                self.device1.name,
                datetime.date(2013, 10, 12),
                self.venture2.name,
                self.venture3.name,
            ],
        ])

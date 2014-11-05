# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from ralph_scrooge.management.commands.scrooge_assets_with_devices import (
    Command
)
from ralph_assets.tests.utils.assets import DCAssetFactory


class TestScroogeAssetModelsCommand(TestCase):
    def setUp(self):
        self.asset = DCAssetFactory()
        self.ralph_device = self.asset.get_ralph_device()

    def test_get_device_name_from_asset_when_device_info_is_null(self):
        self.asset.device_info = None
        self.assertEqual(
            Command().get_device_name_from_asset(
                self.asset,
                {1: 'test0'}
            ),
            None,
        )

    def test_get_device_name_from_asset_when_ralph_id_is_null(self):
        self.asset.device_info.ralph_device_id = None
        self.assertEqual(
            Command().get_device_name_from_asset(
                self.asset,
                {1: 'test0'}
            ),
            None,
        )

    def test_get_device_name_from_asset(self):
        self.assertEqual(
            Command().get_device_name_from_asset(
                self.asset,
                {self.asset.device_info.ralph_device_id: 'test0'}
            ),
            'test0',
        )

    def test_get_device_ids_when_device_info_is_null(self):
        self.asset.device_info = None
        self.assertEqual(Command()._get_device_ids([self.asset]), [])

    def test_get_device_ids(self):
        self.assertEqual(
            Command()._get_device_ids([self.asset]),
            [self.ralph_device.id]
        )

    def test_get_ralph_devices(self):
        self.assertEqual(
            repr(Command()._get_ralph_devices([self.asset])),
            repr([self.ralph_device]),
        )

    def test_get_device_ids_and_names(self):
        self.assertEqual(
            Command().get_device_ids_and_names([self.asset]),
            {self.ralph_device.id: self.ralph_device.name}
        )

    def test_get_deprecated_date_when_force_deprecation(self):
        self.asset.force_deprecation = True
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            'Deprecated'
        )

    def test_get_deprecated_date_when_no_invoice_date(self):
        self.asset.invoice_date = None
        self.asset.save()
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            'No invoice date'
        )

    def test_get_deprecated_date_when_deprecation_end_date(self):
        self.asset.invoice_date = datetime.date.today()
        self.asset.deprecation_rate = 25
        self.asset.deprecation_end_date = datetime.date.today()
        self.asset.save()
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            datetime.date.today()
        )

    def test_get_deprecated_date(self):
        self.asset.invoice_date = datetime.date.today()
        self.asset.deprecation_end_date = None
        self.asset.deprecation_rate = 25
        self.asset.save()
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            datetime.date.today() + relativedelta(years=4)
        )

    def test_get_data(self):
        self.assertEqual(
            Command().get_data(),
            [[
                self.asset.id,
                self.asset.sn,
                self.asset.barcode,
                self.asset.venture.name,
                self.asset.get_ralph_device().name,
                self.asset.deprecation_end_date,
            ]]
        )

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from mock import patch, Mock

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from ralph_pricing.management.commands.pricing_assets_with_devices import (
    Command
)
from ralph_assets.models import (
    Asset,
    DeviceInfo,
    Warehouse,
    AssetType,
    AssetModel,
)
from ralph.discovery.models import Device as RalphDevice


class TestAssetsWithDeviceAndDeprecationEndCommand(TestCase):
    def setUp(self):
        self.ralph_device = RalphDevice.objects.create(
            name="Name0",
        )
        self.device_info = DeviceInfo.objects.create(
            ralph_device_id=1,
        )
        self.asset = Asset.objects.create(
            device_info=self.device_info,
            type=AssetType.data_center,
            model=AssetModel.objects.create(),
            warehouse=Warehouse.objects.create()
        )

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
                {1: 'test0'}
            ),
            'test0',
        )

    def test_get_device_ids_when_device_info_is_null(self):
        self.asset.device_info = None
        self.assertEqual(Command()._get_device_ids([self.asset]), [])

    def test_get_device_ids(self):
        self.assertEqual(Command()._get_device_ids([self.asset]), [1])

    @patch.object(Command, '_get_device_ids', Mock(return_value=[1]))
    def test_get_ralph_devices(self):
        self.assertEqual(
            repr(Command()._get_ralph_devices([self.asset])),
            repr([self.ralph_device]),
        )

    def test_get_device_ids_and_names(self):
        Command._get_ralph_devices = Mock(return_value=[self.ralph_device])
        self.assertEqual(
            Command().get_device_ids_and_names([self.asset]),
            {1: 'Name0'}
        )

    def test_get_deprecated_date_when_force_deprecation(self):
        self.asset.force_deprecation = True
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            'Deprecated'
        )

    def test_get_deprecated_date_when_no_invoice_date(self):
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            'No invoice date'
        )

    def test_get_deprecated_date_when_deprecation_end_date(self):
        self.asset.invoice_date = datetime.date.today()
        self.asset.deprecation_end_date = datetime.date.today()
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            datetime.date.today()
        )

    def test_get_deprecated_date(self):
        self.asset.invoice_date = datetime.date.today()
        self.asset.deprecation_rate = 25
        self.assertEqual(
            Command().get_deprecated_date(self.asset),
            datetime.date.today() + relativedelta(years=4)
        )

    def test_handle(self):
        Command.render = Mock()
        Command().handle(None)
        Command.render.assert_called_once_with(
            [u'Asset ID: 1, Asset SN: None, Asset barcode: None, '
             'Venture: None, Device Name: Name0, Deprecated date: '
             'No invoice date'],
            None
        )

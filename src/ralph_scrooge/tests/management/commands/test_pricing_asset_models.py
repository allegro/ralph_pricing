# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase

from ralph_scrooge.management.commands.pricing_asset_models import (
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


class TestPricingBaseCommand(TestCase):
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

    def test_get_data(self):
        self.assertEqual(
            Command().get_data(),
            [[u'', None, None, 0, 0.0, 0, None, 1]],
        )

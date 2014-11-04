# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase

from ralph_scrooge.management.commands.scrooge_asset_models import (
    Command
)
from ralph_assets.models import DeviceInfo
from ralph_assets.tests.utils.assets import DCAssetFactory
from ralph.discovery.models import Device as RalphDevice


class TestScroogeBaseCommand(TestCase):
    def setUp(self):
        self.ralph_device = RalphDevice.objects.create(
            name="Name0",
        )
        self.device_info = DeviceInfo.objects.create(
            ralph_device_id=1,
        )
        self.asset = DCAssetFactory()

    def test_get_data(self):
        self.assertEqual(
            Command().get_data(),
            [[
                self.asset.model.name,
                self.asset.model.manufacturer.name,
                self.asset.model.category.name,
                self.asset.model.power_consumption,
                self.asset.model.height_of_device,
                self.asset.model.cores_count,
                self.asset.model.type,
                1,
            ]],
        )

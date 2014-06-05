# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dateutil.relativedelta import relativedelta

from ralph.discovery.models import Device
from ralph_assets.models import Asset, AssetType
from ralph_pricing.management.commands.pricing_base import PricingBaseCommand


logger = logging.getLogger(__name__)


class Command(PricingBaseCommand):
    """Generate report with assets, devices and date of end deprecation"""
    CSV_HEADERS = ['Asset ID', 'Asset SN', 'Device Name', 'Deprecated date']
    TEMPLATES = {
        'csv': '{0};{1};{2};{3}',
        'default': ('Asset ID: {0}, Asset SN: {1}, Device Name: {2}'
                    ' Deprecated date: {3}'),
    }

    def handle(self, file_path, *args, **options):
        """
        Collect assets from data center and match it to devices from ralph.
        Calculate date of end deprecation.

        :param string file_path: path to file
        """
        _template, results = self._get_template(options)
        assets = Asset.objects.filter(type=AssetType.data_center)
        devices = self.get_device_ids_and_names(assets)

        for asset in assets:
            results.append(
                _template.format(
                    asset.id,
                    asset.sn,
                    self.get_device_name_from_asset(asset, devices),
                    self.get_deprecated_date(asset),
                )
            )

        self.render(results, file_path)

    def get_device_name_from_asset(self, asset, devices):
        """
        Choose template and create results container. For example csv
        require headers.

        :param object asset: Single asset object
        :param dict devices: Dict with device id as key and name as value
        :returns string: name of device or None
        :rtype string:
        """
        if asset.device_info and asset.device_info.ralph_device_id:
            return devices[asset.device_info.ralph_device_id]

    def _get_device_ids(self, assets):
        """
        Create list of device id matched with assets.

        :param object assets: Assets for which device ids will return
        :returns list: List of device ids
        :rtype list:
        """
        device_ids = []
        for asset in assets:
            if asset.device_info:
                device_ids.append(asset.device_info.ralph_device_id)
        return device_ids

    def _get_ralph_devices(self, assets):
        """
        Get ralph devices.

        :param object assets: Assets for which device ids will return
        :returns list: List of devices from ralph
        :rtype list:
        """
        return Device.objects.filter(
            id__in=self._get_device_ids(assets)
        )

    def get_device_ids_and_names(self, assets):
        """
        Generate dict with device id as a name and device name as value

        :param object assets: Assets for which device ids will return
        :returns list: List of device ids and names
        :rtype list:
        """
        devices = {}
        for device in self._get_ralph_devices(assets):
            devices[device.id] = device.name
        return devices

    def get_deprecated_date(self, asset):
        """
        Calculate end deprecation date for single asset

        :param object asset: Single asset
        :returns string: Date of end deprecation or message
        :rtype string:
        """
        if asset.force_deprecation:
            return 'Deprecated'
        if not asset.invoice_date:
            return 'No invoice date'
        if asset.deprecation_end_date:
            return asset.deprecation_end_date
        else:
            return asset.invoice_date + relativedelta(
                months=asset.get_deprecation_months(),
            )

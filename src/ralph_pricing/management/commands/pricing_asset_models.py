# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from dateutil.relativedelta import relativedelta

from ralph.discovery.models import Device
from ralph_assets.models import AssetModel, Asset
from ralph_pricing.management.commands.pricing_base import PricingBaseCommand


logger = logging.getLogger(__name__)


class Command(PricingBaseCommand):
    """Generate report with assets, devices and date of end deprecation"""
    CSV_HEADERS = [
        'Asset Model Name',
        'Manufacturer',
        'Category',
        'Power consumption',
        'Height of device',
        'Cores count',
        'Type',
        'Assets count',
    ]
    TEMPLATES = {
        'csv': '{0};{1};{2};{3};{4};{5};{6};{7}',
        'default': '{0};{1};{2};{3};{4};{5};{6};{7}',
    }

    def handle(self, file_path, *args, **options):
        """
        Collect assets from data center and match it to devices from ralph.
        Calculate date of end deprecation.

        :param string file_path: path to file
        """
        _template, results = self._get_template(options)
        asset_models = AssetModel.objects.all()

        for asset_model in asset_models:
            results.append(
                _template.format(
                    asset_model.name,
                    asset_model.manufacturer,
                    asset_model.category,
                    asset_model.power_consumption,
                    asset_model.height_of_device,
                    asset_model.cores_count,
                    asset_model.type,
                    Asset.objects.filter(model=asset_model).count(),
                )
            )

        self.render(results, file_path)
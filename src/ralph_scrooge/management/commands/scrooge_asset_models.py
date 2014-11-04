# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.models import Count

from ralph_assets.models import AssetModel
from ralph_scrooge.management.commands._scrooge_base import ScroogeBaseCommand


logger = logging.getLogger(__name__)


class Command(ScroogeBaseCommand):
    """
    Generate report with assets and devices matching and basic information
    about asset, such as cores count, model name etc.
    """
    HEADERS = [
        'Asset Model Name',
        'Manufacturer',
        'Category',
        'Power consumption',
        'Height of device',
        'Cores count',
        'Type',
        'Assets count',
    ]

    def get_data(self, *args, **options):
        """
        Collect assets from data center and match it to devices from ralph.
        Calculate date of end deprecation.

        :param string file_path: path to file
        """
        results = []
        asset_models = AssetModel.objects.annotate(
            assets_count=Count('assets'),
        )
        for asset_model in asset_models:
            results.append([
                asset_model.name,
                asset_model.manufacturer.name,
                asset_model.category.name,
                asset_model.power_consumption,
                asset_model.height_of_device,
                asset_model.cores_count,
                asset_model.type,
                asset_model.assets_count,
            ])
        return results

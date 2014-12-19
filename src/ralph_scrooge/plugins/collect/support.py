# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph_assets.api_scrooge import get_supports
from ralph_scrooge.models import (
    AssetInfo,
    SupportCost,
)


logger = logging.getLogger(__name__)


def update_support(data):
    """
    Update information about asset support

    :param dict data: dict with information about single asset support
    :returns int: number of assets, for which support was saved
    :rtype int:
    """
    assets_count = 0
    if data['assets']:
        asset_support_price = data['price'] / len(data['assets'])
        support_ids = set()
        for asset in data['assets']:
            try:
                asset_info = AssetInfo.objects.get(asset_id=asset)
            except AssetInfo.DoesNotExist:
                logger.error('Asset not found: {}'.format(asset))
                continue
            assets_count += 1
            support, created = SupportCost.objects.get_or_create(
                support_id=data['support_id'],
                pricing_object=asset_info,
                defaults=dict(
                    start=data['date_from'],
                    end=data['date_to'],
                    cost=asset_support_price,
                    forecast_cost=asset_support_price,
                    remarks=data['name'],
                )
            )
            support.cost = asset_support_price
            support.forecast_cost = asset_support_price
            support.start = data['date_from']
            support.end = data['date_to']
            support.remarks = data['name']
            support.save()
            support_ids.add(support.id)
        SupportCost.objects.filter(
            support_id=data['support_id']
        ).exclude(
            id__in=support_ids
        ).delete()
    return assets_count


@plugin.register(chain='scrooge', requires=['asset'])
def support(today, **kwargs):
    """
    Get all information about assets supports

    :returns tuple: result status, message
    """
    total = assets = 0
    for support in get_supports(today):
        total += 1
        assets += update_support(support)

    return True, 'Supports: {} total (for {} assets)'.format(
        total,
        assets,
    )

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph.util.api_scrooge import get_fc_cards
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    UsageType,
)

logger = logging.getLogger(__name__)


class AssetInfoNotFound(Exception):
    pass


class DailyAssetInfoNotFound(Exception):
    pass


def update_usage(daily_asset_info, date, value, usage_type):
    """
    Saves single record to model
    """
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        daily_pricing_object=daily_asset_info,
        defaults=dict(
            service_environment=daily_asset_info.service_environment,
        )
    )
    usage.service_environment = daily_asset_info.service_environment
    usage.value = value
    usage.save()
    return created


def update_san(data, date, usage_type):
    """
    Updates single SAN usage type record
    """
    try:
        asset_info = AssetInfo.objects.get(device_id=data['device_id'])
        daily_asset_info = asset_info.dailyassetinfo_set.get(date=date)
        return update_usage(
            daily_asset_info,
            date,
            1,
            usage_type,
        )
    except AssetInfo.DoesNotExist:
        raise AssetInfoNotFound()
    except DailyAssetInfo.DoesNotExist:
        raise DailyAssetInfoNotFound()


def get_usage_type():
    """
    Returns SAN usage type
    """
    return UsageType.objects.get_or_create(
        symbol='san',
        defaults=dict(
            name='SAN',
        )
    )[0]


@plugin.register(chain='scrooge', requires=['asset', 'service'])
def san(today, **kwargs):
    """
    Updates SAN usages from Ralph
    """
    usage_type = get_usage_type()
    new_san = updated = total = 0
    for data in get_fc_cards():
        try:
            if update_san(data, today, usage_type):
                new_san += 1
            else:
                updated += 1
        except AssetInfoNotFound:
            logger.warning('Device {} not found'.format(data['device_id']))
        except DailyAssetInfoNotFound:
            logger.warning(
                'DailyAssetInfo for id {} and date {} not found'.format(
                    data['device_id'],
                    today,
                )
            )
        total += 1
    return (
        True,
        '{} new SAN usages, {} updated, {} total'.format(
            new_san,
            updated,
            total,
        )
    )

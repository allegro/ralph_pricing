# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph.util.api_scrooge import get_blade_servers
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    UsageType,
)

logger = logging.getLogger(__name__)


class AssetInfoNotFoundError(Exception):
    pass


class DailyAssetInfoNotFoundError(Exception):
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


def update_blade_server(data, date, usage_type):
    """
    Updates single Blade Server usage type record
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
        raise AssetInfoNotFoundError()
    except DailyAssetInfo.DoesNotExist:
        raise DailyAssetInfoNotFoundError()


def get_usage_type():
    """
    Returns Blade Server usage type
    """
    return UsageType.objects.get_or_create(
        symbol='blade_server',
        defaults=dict(
            name='Blade server',
        )
    )[0]


@plugin.register(chain='scrooge', requires=['asset', 'service'])
def blade_server(today, **kwargs):
    """
    Updates Blade Servers usages from Ralph
    """
    usage_type = get_usage_type()
    new_blades = updated = total = 0
    for data in get_blade_servers():
        try:
            if update_blade_server(data, today, usage_type):
                new_blades += 1
            else:
                updated += 1
        except AssetInfoNotFoundError:
            logger.warning('Device {} not found'.format(data['device_id']))
        except DailyAssetInfoNotFoundError:
            logger.warning(
                'DailyAssetInfo for id {} and date {} not found'.format(
                    data['device_id'],
                    today,
                )
            )
        total += 1
    return (
        True,
        '{} new Blade Servers usages, {} updated, {} total'.format(
            new_blades,
            updated,
            total,
        )
    )

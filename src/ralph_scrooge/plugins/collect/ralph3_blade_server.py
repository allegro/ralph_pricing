# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    UsageType
)
from ralph_scrooge.plugins.collect.ralph3_asset import (
    should_be_handled_by_scrooge
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph

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
        asset_info = AssetInfo.objects.get(ralph3_asset_id=data['id'])
        daily_asset_info = asset_info.dailyassetinfo_set.get(date=date)
        return update_usage(
            daily_asset_info,
            date,
            # we store 1 for each blade server so we're charing each blade
            # server equally here (no matter what resources it have), so
            # basically each service is charged proportionally to the count
            # of blade servers they have
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
    return UsageType.objects_admin.get_or_create(
        symbol='blade_server',
        defaults=dict(
            name='Blade server',
        )
    )[0]


@plugin.register(
    chain='scrooge', requires=['ralph3_asset', 'ralph3_service_environment']
)
def ralph3_blade_server(today, **kwargs):
    """
    Updates Blade Servers usages from Ralph
    """
    if not settings.RALPH3_BLADE_SERVER_CATEGORY_ID:
        msg = 'RALPH3_BLADE_SERVER_CATEGORY_ID not set'
        logger.error(msg)
        return (False, msg)
    usage_type = get_usage_type()
    new_blades = updated = total = errors = 0
    for asset in get_from_ralph(
        'data-center-assets', logger, query='model__category={}'.format(
            settings.RALPH3_BLADE_SERVER_CATEGORY_ID
        )
    ):
        if not should_be_handled_by_scrooge(asset):
            continue
        total += 1
        try:
            if update_blade_server(asset, today, usage_type):
                new_blades += 1
            else:
                updated += 1
        except:
            logger.exception(
                'Exception during processing blade server: {}'.format(
                    asset['__str__']
                )
            )
            errors += 1
    return (
        True,
        '{} new Blade Servers usages, {} updated, {} errors, {} total'.format(
            new_blades, updated, errors, total,
        )
    )

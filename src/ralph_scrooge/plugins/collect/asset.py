# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_assets.api_pricing import get_assets
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    PricingObject,
    DailyPricingObject,
    Service,
    DailyUsage,
    UsageType,
    Warehouse,
)


logger = logging.getLogger(__name__)


def create_pricing_object(service, data):
    return PricingObject.objects.create(
        name=data['asset_name'],
        service=service,
        type=0,
    )


def get_asset_and_pricing_object(service, warehouse, data):
    created = False
    try:
        asset_info = AssetInfo.objects.get(asset_id=data['asset_id'])
    except AssetInfo.DoesNotExist:
        asset_info = AssetInfo.objects.create(
            asset_id=data['asset_id'],
            pricing_object=create_pricing_object(service, data),
            warehouse = warehouse,
        )
        created = True
    asset_info.sn = data['sn']
    asset_info.barcode = data['barcode']
    asset_info.device_id = data['device_id']
    return asset_info, asset_info.pricing_object, created


def get_daily_pricing_object(pricing_object, service, date):
    # DailyPricingObject
    return DailyPricingObject.objects.get_or_create(
        pricing_object=pricing_object,
        date=date,
        service=service,
    )


def get_daily_asset_info(asset_info, daily_pricing_object, date, data):
    daily_asset_info, created = AssetInfo.objects.get_or_create(
        asset_info=asset_info,
        daily_pricing_object=daily_pricing_object,
        date=date,
    )
    daily_asset_info.depreciation_rate = date['depreciation_rate']
    daily_asset_info.is_depreciated = date['is_deprecated']
    daily_asset_info.daily_cost = date['daily_cost']
    daily_asset_info.save()
    return daily_asset_info, created


def update_usage(service, pricing_object, type, value, date, warehouse):
    """Updates (or creates) usage of given usage_type for device."""
    usage, usage_created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        daily_pricing_object=pricing_object,
        service=service,
        warehouse=warehouse,
    )
    usage.value = value
    usage.save()


@commit_on_success
def update_assets(data, date, usages):
    """
    Updates single asset.

    Creates asset (Device object for backward compatibility) if not exists,
    then creates daily snapshot of this device.

    Only assets with assigned device and warehouse are processed!
    """
    try:
        service = Service.objects.get(ci_uid=data['service_ci_uid'])
    except Service.DoesNotExist:
        logger.error('Service {0} does not exist'.format(
            data['service_ci_uid'],
        ))
        return (False, False)

    try:
        warehouse = Warehouse.objects.get(id_from_assets=data['warehouse_id'])
    except Warehouse.DoesNotExist:
        logger.error('Warehouse {0} does not exist'.format(
            data['warehouse_id']
        ))
        return (False, False)

    pricing_object, asset_info, new_created = get_asset_and_pricing_object(
        service,
        warehouse,
        data,
    )
    daily_pricing_object, created = get_daily_pricing_object(
        pricing_object,
        service,
        date,
    )
    daily_asset_info, created = get_daily_asset_info(
        asset_info,
        daily_pricing_object,
        date,
        data,
    )

    update_usage(
        service,
        daily_pricing_object,
        usages['core'],
        data['core'],
        date,
        warehouse,
    )
    update_usage(
        service,
        daily_pricing_object,
        usages['power_consumption'],
        data['power_consumption'],
        date,
        warehouse,
    )
    update_usage(
        service,
        daily_pricing_object,
        usages['collocation'],
        data['collocation'],
        date,
        warehouse,
    )
    return (True, new_created)


def get_usage(symbol, name, by_warehouse, by_cost, average):
    """Creates power consumption usage type if not created."""
    usage_type, created = UsageType.objects.get_or_create(
        symbol=symbol,
        defaults=dict(
            name=name,
            by_warehouse=by_warehouse,
            by_cost=by_cost,
            average=average,
        ),
    )
    return usage_type


@plugin.register(chain='pricing', requires=[])
def asset(**kwargs):
    """
    Updates assets and usages
    :returns tuple: Plugin status and statistics
    :rtype typle:
    """
    date = kwargs['today']
    usages = {
        'core': get_usage(
            'physical_cpu_cores',
            'Physical CPU cores',
            False,
            False,
            True,
        ),
        'power_consumption': get_usage(
            'power_consumption',
            'Power consumption',
            True,
            True,
            False,
        ),
        'collocation': get_usage(
            'collection',
            'Collection',
            True,
            True,
            False,
        ),
    }

    new = update = total = 0
    for data in get_assets(date):
        result = update_assets(data, date, usages)
        if result[0]:
            if result[1]:
                new += int(result[1])
            else:
                update += int(result[1])
        total += 1

    return True, '{0} new, {1} updated, {2} total'.format(new, update, total)

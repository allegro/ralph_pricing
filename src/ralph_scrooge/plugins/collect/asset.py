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
    DailyUsage,
    DailyPricingObject,
    PricingObject,
    PricingObjectType
    Service,
    UsageType,
    Warehouse,
)


logger = logging.getLogger(__name__)


def create_pricing_object(service, data):
    """
    Create pricing object

    :param object service: Django orm Service object
    :param dict data: Data from assets API
    :returns object: Django orm PricingObject object
    :rtype:
    """
    return PricingObject.objects.create(
        name=data['asset_name'],
        service=service,
        type=PricingObjectType.asset,
    )


def get_asset_and_pricing_object(service, warehouse, data):
    """
    Update AssetInfo object or create it if not exist.

    :param object service: Django orm Service object
    :param object warehouse: Django orm Warehouse object
    :param dict data: Data from assets API
    :returns list: AssetInfo PricingObject and status
    :rtype:
    """
    created = False
    try:
        asset_info = AssetInfo.objects.get(asset_id=data['asset_id'])
        asset_info.pricing_object.service = service
        asset_info.pricing_object.name = data['asset_name']
        asset_info.pricing_object.save()
    except AssetInfo.DoesNotExist:
        asset_info = AssetInfo.objects.create(
            asset_id=data['asset_id'],
            pricing_object=create_pricing_object(service, data),
        )
        created = True
    asset_info.warehouse = warehouse
    asset_info.sn = data['sn']
    asset_info.barcode = data['barcode']
    asset_info.device_id = data['device_id']
    asset_info.save()
    return asset_info, asset_info.pricing_object, created


def get_daily_pricing_object(pricing_object, service, date):
    """
    Create daily pricing object

    :param object service: Django orm Service object
    :param object warehouse: Django orm Warehouse object
    :param object date: datetime
    :returns object: Django orm DailyPricingObject object
    :rtype:
    """
    daily_pricing_object = DailyPricingObject.objects.get_or_create(
        pricing_object=pricing_object,
        date=date,
    )[0]
    daily_pricing_object.service = service
    daily_pricing_object.save()
    return daily_pricing_object


def get_daily_asset_info(asset_info, daily_pricing_object, date, data):
    """
    Get or create daily asset info

    :param object asset_info: Django orm AssetInfo object
    :param object daily_pricing_object: Django orm DailyPricingObject object
    :param object date: datetime
    :param dict data: Data from assets API
    :returns list: Django orm DailyAssetInfo object
    :rtype:
    """
    daily_asset_info, created = DailyAssetInfo.objects.get_or_create(
        asset_info=asset_info,
        daily_pricing_object=daily_pricing_object,
        date=date,
    )
    daily_asset_info.depreciation_rate = data['depreciation_rate']
    daily_asset_info.is_depreciated = data['is_depreciated']
    daily_asset_info.price = data['price']
    daily_asset_info.save()
    return daily_asset_info


def update_usage(service, pricing_object, usage_type, value, date, warehouse):
    """
    Updates (or creates) usage of given usage_type for device.

    :param object service: Django orm Service object
    :param object pricing_object: Django orm PricingObject object
    :param object usage_type: Django orm UsageType object
    :param object value: value from asset api for given usage type
    :param object date: datetime
    :param object warehouse: Django orm Warehouse object
    """
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

    :param object date: datetime
    :param dict data: Data from assets API
    :param dict usages: Dict with usage types from Django orm UsageType
    :returns tuple: Success for this update and information about
                    create or update
    :rtype tuple:
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

    asset_info, pricing_object, new_created = get_asset_and_pricing_object(
        service,
        warehouse,
        data,
    )
    daily_pricing_object = get_daily_pricing_object(
        pricing_object,
        service,
        date,
    )
    get_daily_asset_info(
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
    """
    Creates power consumption usage type if not created.

    :param string symbol: Symbol name
    :param string name: Usage type name
    :param boolean by_warehouse: Flag by_warehouse
    :param boolean by_cost: Flag by_cost
    :param boolean average: Flag average
    :returns object: Django orm UsageType object
    :rtype object:
    """
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
    :rtype tuple:
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
                new += 1
            else:
                update += 1
        total += 1

    return True, '{0} new, {1} updated, {2} total'.format(new, update, total)

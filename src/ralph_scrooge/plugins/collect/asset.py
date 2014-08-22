# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from decimal import Decimal as D

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_assets.api_pricing import get_assets
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    PricingObjectType,
    ServiceEnvironment,
    UsagePrice,
    UsageType,
    Warehouse,
)


logger = logging.getLogger(__name__)


class ServiceEnvironmentDoesNotExistError(Exception):
    """
    Raise this exception when service does not exist
    """
    pass


class WarehouseDoesNotExistError(Exception):
    """
    Raise this exception when warehouse does not exist
    """
    pass


def get_asset_info(service_environment, warehouse, data):
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
    except AssetInfo.DoesNotExist:
        asset_info = AssetInfo(
            asset_id=data['asset_id'],
            type=PricingObjectType.asset,
        )
        created = True
    asset_info.service_environment = service_environment
    asset_info.name = data['asset_name']
    asset_info.warehouse = warehouse
    asset_info.sn = data['sn']
    asset_info.barcode = data['barcode']
    asset_info.device_id = data['device_id']
    asset_info.save()
    return asset_info, created


def get_daily_asset_info(asset_info, date, data):
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
        pricing_object=asset_info,
        asset_info=asset_info,
        date=date,
        defaults=dict(
            service_environment=asset_info.service_environment,
        ),
    )
    # set defaults if daily asset was not created
    daily_asset_info.service_environment = asset_info.service_environment
    daily_asset_info.depreciation_rate = data['depreciation_rate']
    daily_asset_info.is_depreciated = data['is_depreciated']
    daily_asset_info.price = data['price']
    daily_asset_info.save()
    return daily_asset_info


def update_usage(daily_asset_info, warehouse, usage_type, value, date):
    """
    Updates (or creates) usage of given usage_type for device.

    :param object service: Django orm Service object
    :param object pricing_object: Django orm PricingObject object
    :param object usage_type: Django orm UsageType object
    :param object value: value from asset api for given usage type
    :param object date: datetime
    :param object warehouse: Django orm Warehouse object
    """
    defaults = dict(
        service_environment=daily_asset_info.service_environment,
        warehouse=warehouse,
    )
    usage, usage_created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        daily_pricing_object=daily_asset_info,
        defaults=defaults
    )
    # set defaults if daily usage was not created
    if not usage_created:
        for attr, value in defaults.iteritems():
            setattr(usage, attr, value)
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
        service_environment = ServiceEnvironment.objects.get(
            service__ci_uid=data['service_ci_uid'],
            environment__environment_id=data['environment_id'],
        )
    except ServiceEnvironment.DoesNotExist:
        raise ServiceEnvironmentDoesNotExistError()

    try:
        warehouse = Warehouse.objects.get(id_from_assets=data['warehouse_id'])
    except Warehouse.DoesNotExist:
        raise WarehouseDoesNotExistError()

    asset_info, new_created = get_asset_info(
        service_environment,
        warehouse,
        data,
    )
    daily_asset_info = get_daily_asset_info(
        asset_info,
        date,
        data,
    )

    update_usage(
        daily_asset_info,
        warehouse,
        usages['depreciation'],
        daily_asset_info.daily_cost,
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['assets_count'],
        1,
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['cores_count'],
        data['cores_count'],
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['power_consumption'],
        data['power_consumption'],
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['collocation'],
        data['collocation'],
        date,
    )
    return new_created


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
    # TODO: add types (BU, SU)
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


@plugin.register(
    chain='scrooge',
    requires=['service', 'environment', 'warehouse']
)
def asset(**kwargs):
    """
    Updates assets and usages

    :returns tuple: Plugin status and statistics
    :rtype tuple:
    """
    date = kwargs['today']
    depreciation_usage = get_usage(
        'depreciation',
        'Depreciation',
        by_warehouse=False,
        by_cost=False,
        average=True,
    )
    try:
        usage_price = UsagePrice.objects.get(
            type=depreciation_usage
        )
    except UsagePrice.DoesNotExist:
        usage_price = UsagePrice(type=depreciation_usage)
    usage_price.start = date.min
    usage_price.end = date.max
    usage_price.price = D('1')
    usage_price.forecast_price = D('1')
    usage_price.save()

    usages = {
        'depreciation': depreciation_usage,
        'assets_count': get_usage(
            'assets_count',
            'Assets Count',
            by_warehouse=False,
            by_cost=False,
            average=True,
        ),
        'cores_count': get_usage(
            'physical_cpu_cores',
            'Physical CPU cores',
            by_warehouse=False,
            by_cost=False,
            average=True,
        ),
        'power_consumption': get_usage(
            'power_consumption',
            'Power consumption',
            by_warehouse=True,
            by_cost=True,
            average=False,
        ),
        'collocation': get_usage(
            'collocation',
            'Collocation',
            by_warehouse=True,
            by_cost=True,
            average=True,
        ),
    }

    new = update = total = 0
    for data in get_assets(date):
        total += 1
        try:
            if update_assets(data, date, usages):
                new += 1
            else:
                update += 1
        except ServiceEnvironmentDoesNotExistError:
            logger.error(
                'Asset {}: Service environment {} - {} does not exist'.format(
                    data['asset_id'],
                    data['service_ci_uid'],
                    data['environment_id'],
                )
            )
            continue
        except WarehouseDoesNotExistError:
            logger.error('Warehouse {0} does not exist'.format(
                data['warehouse_id']
            ))
            continue

    return True, '{0} new, {1} updated, {2} total'.format(new, update, total)

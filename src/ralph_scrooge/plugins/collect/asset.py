# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from decimal import Decimal as D

from django.db import IntegrityError
from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_scrooge.models import (
    AssetInfo,
    DailyAssetInfo,
    DailyUsage,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    UsagePrice,
    UsageType,
    Warehouse,
)
from ralph_scrooge.plugins.collect._exceptions import (
    ServiceEnvironmentDoesNotExistError,
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


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
        asset_info = AssetInfo.objects.get(asset_id=data['id'])
    except AssetInfo.DoesNotExist:
        asset_info = AssetInfo(
            asset_id=data['id'],
            type_id=PRICING_OBJECT_TYPES.ASSET,
        )
        created = True
    asset_info.service_environment = service_environment
    asset_info.name = data['hostname']
    asset_info.warehouse = warehouse
    asset_info.sn = data['sn']
    asset_info.barcode = data['barcode']
    asset_info.device_id = data['id']
    try:
        asset_info.save()
    except IntegrityError:
        # check for duplicates on SN, barcode and device_id, null them and save
        # again
        for field in ['sn', 'barcode', 'device_id']:  # XXX device_id is id in data, so we cannot use this name for both
            assets = AssetInfo.objects.filter(**{field: data[field]}).exclude(
                asset_id=data['id'],
            )
            for asset in assets:
                logger.error('Duplicated {} ({}) on assets {} and {}'.format(
                    field,
                    data[field],
                    data['asset_id'],
                    asset.asset_id,
                ))
                setattr(asset, field, None)
                asset.save()
        # save new asset again
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
    # daily_asset_info.is_depreciated = data['is_depreciated']  # XXX we doesn't have such field in R3's API
    daily_asset_info.price = data['price'] or 0
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
            # XXX same situation as with tenant plugin:
            # - should we get service env by service_id && env_id..?
            # - what if service env will be empty?
            id=data['service_env']['id']
        )
    except ServiceEnvironment.DoesNotExist:
        raise ServiceEnvironmentDoesNotExistError()

    try:
        dc_id = data['rack']['server_room']['data_center']['id']  # XXX OK?
        warehouse = Warehouse.objects.get(id_from_assets=dc_id)
    except Warehouse.DoesNotExist:
        warehouse = Warehouse.objects.get(pk=1)  # Default from fixtures

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
        data['model']['cores_count'],
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['power_consumption'],
        data['model']['power_consumption'],
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['collocation'],
        data['collocation'],  # XXX no such field
        date,
    )
    return new_created


def get_usage(symbol, name, by_warehouse, by_cost, average, type):
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
    usage_type, created = UsageType.objects_admin.get_or_create(
        symbol=symbol,
        defaults=dict(
            name=name,
            by_warehouse=by_warehouse,
            by_cost=by_cost,
            average=average,
        ),
    )
    usage_type.usage_type = type
    usage_type.save()
    return usage_type


@plugin.register(
    chain='scrooge',
    requires=['service', 'environment', 'warehouse', 'asset_model']
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
        type='BU',
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
            type='SU',
        ),
        'cores_count': get_usage(
            'physical_cpu_cores',
            'Physical CPU cores count',
            by_warehouse=False,
            by_cost=False,
            average=True,
            type='SU',
        ),
        'power_consumption': get_usage(
            'power_consumption',
            'Power consumption',
            by_warehouse=True,
            by_cost=True,
            average=False,
            type='BU',
        ),
        'collocation': get_usage(
            'collocation',
            'Collocation',
            by_warehouse=True,
            by_cost=True,
            average=True,
            type='BU',
        ),
    }

    new = update = total = 0
    for data in get_from_ralph("data-center-assets", logger): # XXX - what about date parameter, i.e. get_assets(date)..?
        total += 1
        try:
            if update_assets(data, date, usages):
                new += 1
            else:
                update += 1
        except ServiceEnvironmentDoesNotExistError:  # XXX ?
            logger.error(
                'Asset {}: Service environment {} - {} does not exist'.format(
                    data['id'],
                    # XXX don't have these fields
                    # data['service_id'],
                    # data['environment_id'],
                    # using these instead:
                    data['service_env']['service'],
                    data['service_env']['environment'],
                )
            )
            continue

    return True, '{0} new, {1} updated, {2} total'.format(new, update, total)  # XXX

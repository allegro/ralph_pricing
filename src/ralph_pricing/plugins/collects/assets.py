# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_assets.api_pricing import get_assets
from ralph_pricing.models import (
    Device,
    DailyDevice,
    Venture,
    DailyUsage,
    UsageType,
    Warehouse,
)


logger = logging.getLogger(__name__)


@commit_on_success
def update_assets(data, date, usages):
    """
    Updates single asset.

    Creates asset (Device object for backward compatibility) if not exists,
    then creates daily snapshot of this device.

    Only assets with assigned device and warehouse are processed!
    """
    created = False
    if not data['ralph_id']:
        return False

    if not data['warehouse_id']:
        logger.warning(
            'Empty warehouse_id for asset with ralph_id {0}', data['ralph_id']
        )
        return False

    try:
        warehouse = Warehouse.objects.get(
            id=data['warehouse_id'],
        )
    except Warehouse.DoesNotExist:
        logger.warning(
            'Invalid warehouse_id ({0}) for asset with ralph_id {1}',
            data['warehouse_id'],
            data['ralph_id'],
        )
        return False

    # clear previous asset assignments
    # (only if current device_is != previous device_id)
    try:
        old_device = Device.objects.exclude(
            device_id=data['ralph_id'],
        ).get(
            asset_id=data['asset_id'],
        )
    except Device.DoesNotExist:
        pass
    else:
        old_device.asset_id = None
        old_device.save()

    # get or create asset
    try:
        device = Device.objects.get(asset_id=data['asset_id'])
    except Device.DoesNotExist:
        try:
            device = Device.objects.get(sn=data['sn'])
        except Device.DoesNotExist:
            created = True
            device = Device()
            device.device_id = data['ralph_id']

    # device info
    device.asset_id = data['asset_id']
    device.slots = data['slots']
    device.sn = data['sn']
    device.barcode = data['barcode']
    device.is_blade = data['is_blade']
    device.save()

    # daily device 'snapshot'
    daily_device, daily_device_created = DailyDevice.objects.get_or_create(
        date=date,
        pricing_device=device,
    )
    if data.get('venture_id') is not None:
        venture, venture_created = Venture.objects.get_or_create(
            venture_id=data['venture_id'],
        )
        daily_device.pricing_venture = venture
    else:
        logger.warning('Asset {0} has no venture'.format(data['asset_id']))
        return False

    daily_device.price = data['price']
    daily_device.deprecation_rate = data['deprecation_rate']
    daily_device.is_deprecated = data['is_deprecated']
    daily_device.save()

    # cores count usage
    update_usage(
        data['cores_count'],
        date,
        daily_device.pricing_venture,
        warehouse,
        usages['core'],
        device,
    )

    # power consumption usage
    update_usage(
        data['power_consumption'],
        date,
        daily_device.pricing_venture,
        warehouse,
        usages['power_consumption'],
        device,
    )

    # height of device usage
    update_usage(
        data['height_of_device'],
        date,
        daily_device.pricing_venture,
        warehouse,
        usages['height_of_device'],
        device,
    )

    return created


def update_usage(value, date, venture, warehouse, usage_type, device):
    """Updates (or creates) usage of given usage_type for device."""
    usage, usage_created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
    )
    if venture is not None:
        usage.pricing_venture = venture
    if usage_type.by_warehouse and warehouse is not None:
        usage.warehouse = warehouse
    usage.value = value
    usage.save()


def get_core_usage():
    """Creates physical cpu cores usage type if not created."""
    usage_type, created = UsageType.objects.get_or_create(
        name="Physical CPU cores",
        symbol='physical_cpu_cores',
        average=True,
    )
    usage_type.save()
    return usage_type


def get_power_consumption_usage():
    """Creates power consumption usage type if not created."""
    usage_type, created = UsageType.objects.get_or_create(
        name="Power consumption",
        symbol='power_consumption',
        by_warehouse=True,
        by_cost=True,
    )
    return usage_type


def get_height_of_device_usage():
    """Creates power consumption usage type if not created."""
    usage_type, created = UsageType.objects.get_or_create(
        name="Height of Device",
        symbol='height_of_device',
        by_warehouse=True,
        by_cost=True,
    )
    return usage_type


@plugin.register(chain='pricing', requires=['ventures', 'warehouse'])
def assets(**kwargs):
    """Updates the devices from Ralph Assets."""

    date = kwargs['today']
    usages = {
        'core': get_core_usage(),
        'power_consumption': get_power_consumption_usage(),
        'height_of_device': get_height_of_device_usage(),
    }
    count = sum(
        update_assets(
            data,
            date,
            usages,
        )
        for data in get_assets(date)
    )
    return True, '%d new devices' % count, kwargs

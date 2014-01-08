# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_assets.api_pricing import get_assets
from ralph_pricing.models import Device, DailyDevice, Warehouse


logger = logging.getLogger(__name__)


class RalphIdNotDefinedError(Exception):
    '''
        Exception raised when ralph id is not defined in given data
    '''
    pass


class VentureSymbolNotDefinedError(Exception):
    '''
        Exception raised when venture symbol is not defined in given data
    '''
    pass


class WarehouseDoesNotExistError(Exception):
    '''
        Exception raised when warehouse id do not exist in pricing database
    '''
    pass


@commit_on_success
def update_assets(data, date):
    """
    Used by assets plugin. Update pricing device model according to the
    relevant rules.

    :param dict data: Data from assets pricing api
    :param datetime date: Day for which report will be generated

    :returns boolean: count of new created devices
    :rtype boolean:
    """
    if not data['venture_symbol']:
        raise VentureSymbolNotDefinedError()

    try:
        warehouse = Warehouse.objects.get(id=data['warehouse_id'])
    except Warehouse.DoesNotExist:
        raise WarehouseDoesNotExistError()

    created = False
    if not data['ralph_id']:
        raise RalphIdNotDefinedError()
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
    try:
        device = Device.objects.get(device_id=data['ralph_id'])
    except Device.DoesNotExist:
        created = True
        device = Device()
        device.device_id = data['ralph_id']
    device.asset_id = data['asset_id']
    device.slots = data['slots']
    device.power_consumption = data['power_consumption']
    device.venture_symbol = data['venture_symbol']
    device.sn = data['sn']
    device.barcode = data['barcode']
    device.warehouse = warehouse
    device.save()
    daily, daily_created = DailyDevice.objects.get_or_create(
        date=date,
        pricing_device=device,
    )
    daily.price = data['price']
    # This situation can not happen, depreciation rate cannot be None.
    # Solving this problem is in progress
    if not data['deprecation_rate']:
        data['deprecation_rate'] = 0.00
    daily.deprecation_rate = data['deprecation_rate']
    daily.is_deprecated = data['is_deprecated']
    daily.save()
    return created


@plugin.register(chain='pricing', requires=['devices'])
def assets(**kwargs):
    """Updates the devices from Ralph Assets."""

    date = kwargs['today']
    count = 0
    for data in get_assets(date):
        try:
            update_assets(data, date)
            count += 1
        except RalphIdNotDefinedError:
            logger.error('Data from asset do not contains ralph_id')
        except VentureSymbolNotDefinedError:
            logger.error('Data from asset do not contains venture_symbol')
        except WarehouseDoesNotExistError:
            logger.error('Given warehouse do not exist. You need to run '
                         'warehouse plugin first')
    return True, '%d new devices' % count, kwargs

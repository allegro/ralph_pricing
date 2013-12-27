# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_assets.api_pricing import get_assets
from ralph_pricing.models import Device, DailyDevice


@commit_on_success
def update_assets(data, date):
    """
    Used by assets plugin. Update pricing device model according to the
    relevant rules.
    """
    if not data['venture_symbol']:
        return False

    created = False
    if not data['ralph_id']:
        return False
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
    count = sum(update_assets(data, date) for data in get_assets(date))
    return True, '%d new devices' % count, kwargs

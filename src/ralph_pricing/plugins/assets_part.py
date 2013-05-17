# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin
from ralph_assets.api_pricing import get_asset_parts
from ralph_pricing.models import Device, DailyPart


def update_assets_parts(data, date):
    if not data['asset_id'] and date['ralph_id']:
        return False
    device, created = Device.objects.get_or_create(
        device_id=data['ralph_id'],
    )
    daily, created = DailyPart.objects.get_or_create(
        date=date,
        asset_id=data['asset_id'],
        pricing_device_id=device.id,
        price=data['price'],
    )
    daily.name = data['model']
    daily.is_deprecated = data['is_deprecated']
    daily.save()
    return created


@plugin.register(chain='pricing', requires=['sync_devices'])
def sync_assets(**kwargs):
    """Updates the devices from Ralph Assets."""
    date = kwargs['today']
    count = sum(update_assets_parts(data, date) for data in get_asset_parts())
    return True, '%d new devices' % count, kwargs

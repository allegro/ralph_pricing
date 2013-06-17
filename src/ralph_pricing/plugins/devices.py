# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin, api_pricing
from ralph_pricing.models import Device, ParentDevice, Venture, DailyDevice


def update_device(data, date):
    device, created = Device.objects.get_or_create(
        device_id=data['id'],
    )
    device.name = data['name']
    device.sn = data['sn']
    device.barcode = data['barcode']
    device.is_virtual = data['is_virtual']
    device.is_blade = data['is_blade']
    device.save()

    daily, daily_created = DailyDevice.objects.get_or_create(
        date=date,
        pricing_device=device,
    )
    if data.get('parent_id'):
        parent, parent_created = ParentDevice.objects.get_or_create(
            device_id=data['parent_id'],
        )
        daily.parent = parent
    else:
        parent_created = False
    if data.get('venture_id') is not None:
        venture, venture_created = Venture.objects.get_or_create(
            venture_id=data['venture_id'],
        )
        daily.pricing_venture = venture
    daily.name = data['name']
    daily.save()
    return created + parent_created


@plugin.register(chain='pricing', requires=['ventures'])
def devices(**kwargs):
    """Updates the devices from Ralph."""

    date = kwargs['today']
    count = sum(
        update_device(data, date) for data in api_pricing.get_devices()
    )
    return True, '%d new devices' % count, kwargs

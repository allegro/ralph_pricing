# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin, api_pricing
from ralp_pricing.models import Device, Venture


def update_device(data):
    device, created = Device.objects.get_or_create(
        device_id=data['id'],
    )
    device.name = data['name']
    device.is_virtual = data['is_virtual']
    device.is_blade = data['is_blade']
    venture, venture_created = Venture.objects.get_or_create(
        venture_id = data['venture_id']
    )
    device.venture = venture
    parent, parent_created = Device.objects.get_or_create(
        device_id=data['parent_id'],
    )
    return created + parent_created


@plugin.register(chain='pricing', requires=['sync_ventures'])
def sync_devices(**kwargs):
    """Updates the devices from Ralph."""

    count = sum(update_device(data) for data in api_pricing.get_devices())
    return True, '%d new devices' % count, kwargs


# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin, api_pricing
from ralph_pricing.models import UsageType, DailyUsage, Device, DailyDevice


def update_usage(device, venture, usage_name, date, value):
    if not value:
        return
    usage_type, created = UsageType.objects.get_or_create(
        name=usage_name
    )
    usage_type.average = True
    usage_type.save()
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
    )
    usage.pricing_venture = venture
    usage.value = value
    usage.save()


def update(data, date):
    if data.get('mount_device_id') is not None:
        device, created = Device.objects.get_or_create(
            device_id=data['mount_device_id'],
        )
    else:
        return
    try:
        daily_device = device.dailydevice_set.get(date=date)
        venture = daily_device.pricing_venture
    except DailyDevice.DoesNotExist:
        venture = None
    size = data['size'] / data['share_mount_count']
    usage_name = 'Disk Share {0} MB'.format(data['model'])
    update_usage(device, venture, usage_name, date, size)


@plugin.register(chain='pricing', requires=['assets'])
def shares(**kwargs):
    """Updates the disk share usages from Ralph."""

    date = kwargs['today']
    for data in api_pricing.get_shares():
        update(data, date)
    return True, 'disk share usages updated', kwargs

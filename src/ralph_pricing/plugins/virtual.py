# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin, api_pricing
from ralph_pricing.models import UsageType, DailyUsage, Device, Venture


def update_usage(device, venture, usage_type, date, value):
    if not value:
        return
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
    )
    usage.pricing_venture = venture
    usage.value = value
    usage.save()


def update(data, usages, date):
    if data.get('device_id') is not None:
        device, created = Device.objects.get_or_create(
            device_id=data['device_id'],
        )
    else:
        return
    if data.get('venture_id') is not None:
        venture, created = Venture.objects.get_or_create(
            venture_id=data['venture_id'],
        )
    else:
        venture = None
    for key, usage in usages.iteritems():
        update_usage(device, venture, usage, date, data.get(key))

def get_usages():
    cpu_usage, created = UsageType.objects.get_or_create(
        name="Virtual CPU cores",
    )
    cpu_usage.average = True
    cpu_usage.save()
    memory_usage, created = UsageType.objects.get_or_create(
        name="Virtual memory MB",
    )
    memory_usage.average = True
    memory_usage.save()
    disk_usage, created = UsageType.objects.get_or_create(
        name="Virtual disk MB",
    )
    disk_usage.average = True
    disk_usage.save()
    usages = {
        'virtual_cores': cpu_usage,
        'virtual_memory': memory_usage,
        'virtual_disk': disk_usage,
    }
    return usages


@plugin.register(chain='pricing', requires=['devices'])
def virtual_usages(**kwargs):
    """Updates the virtual usages from Ralph."""

    date = kwargs['today']
    usages = get_usages()
    for data in api_pricing.get_virtual_usages():
        update(data, usages, date)
    return True, 'virtual usages updated', kwargs

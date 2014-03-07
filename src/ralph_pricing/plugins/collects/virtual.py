# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings

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


def get_or_create_usages(usage_names):
    cpu_usage, created = UsageType.objects.get_or_create(
        name=usage_names['virtual_cores'],
        symbol=usage_names['virtual_cores'].replace(' ', '_').lower(),
    )
    cpu_usage.average = True
    cpu_usage.save()
    memory_usage, created = UsageType.objects.get_or_create(
        name=usage_names['virtual_memory'],
        symbol=usage_names['virtual_memory'].replace(' ', '_').lower(),
    )
    memory_usage.average = True
    memory_usage.save()
    disk_usage, created = UsageType.objects.get_or_create(
        name=usage_names['virtual_disk'],
        symbol=usage_names['virtual_disk'].replace(' ', '_').lower(),
    )
    disk_usage.average = True
    disk_usage.save()
    usages = {
        'virtual_cores': cpu_usage,
        'virtual_memory': memory_usage,
        'virtual_disk': disk_usage,
    }
    return usages


# virtual usages requires assets plugin to get proper devices
@plugin.register(chain='pricing', requires=['assets'])
def virtual_usages(**kwargs):
    """Updates the virtual usages from Ralph."""

    date = kwargs['today']
    for venture_name in settings.VIRTUAL_VENTURE_NAMES:
        usage_names = {
            'virtual_cores': '{0} Virtual CPU cores'.format(venture_name),
            'virtual_memory': '{0} Virtual memory MB'.format(venture_name),
            'virtual_disk': '{0} Virtual disk MB'.format(venture_name),
        }
        usages = get_or_create_usages(usage_names)
        for data in api_pricing.get_virtual_usages(venture_name):
            update(data, usages, date)
    return True, 'virtual usages updated', kwargs

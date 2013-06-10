# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin, api_pricing
from ralph_pricing.models import UsageType, DailyUsage, Device, Venture


def update_cores(data, usage_type, date):
    if data.get('device_id') is not None:
        device, created = Device.objects.get_or_create(
            device_id=data['device_id'],
        )
    else:
        return
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
    )
    if data.get('venture_id') is not None:
        venture, created = Venture.objects.get_or_create(
            venture_id=data['venture_id'],
        )
        usage.pricing_venture = venture
    usage.value = data['physical_cores']
    usage.save()
    return usage.value

def get_usage():
    usage_type, created = UsageType.objects.get_or_create(
        name="Physical CPU cores",
    )
    usage_type.average = True
    usage_type.save()
    return usage_type


@plugin.register(chain='pricing', requires=['devices'])
def physical_cores(**kwargs):
    """Updates the physical cores from Ralph."""

    date = kwargs['today']
    usage = get_usage()
    count = sum(
        update_cores(data, usage, date)
        for data in api_pricing.get_physical_cores()
    )
    return True, '%d total physical cores' % count, kwargs

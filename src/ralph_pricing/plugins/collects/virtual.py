# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin, api_pricing
from ralph_pricing.models import UsageType, DailyUsage, Device, Venture


logger = logging.getLogger(__name__)


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
        logger.warning('Device {0} has no venture'.format(data['device_id']))
        return
    for key, usage in usages.iteritems():
        update_usage(device, venture, usage, date, data.get(key))


def get_or_create_usages(usage_names):
    cpu_usage, created = UsageType.objects.get_or_create(
        symbol=usage_names['virtual_cores'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_cores'],
            average=True,
        ),
    )
    cpu_usage.save()

    memory_usage, created = UsageType.objects.get_or_create(
        symbol=usage_names['virtual_memory'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_memory'],
            average=True,
        ),
    )
    memory_usage.save()

    disk_usage, created = UsageType.objects.get_or_create(
        symbol=usage_names['virtual_disk'].replace(' ', '_').lower(),
        defaults=dict(
            name=usage_names['virtual_disk'],
            average=True,
        ),
    )
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
    virtual_venture_names = settings.VIRTUAL_VENTURE_NAMES
    # key in dict is group name (which is propagated to usages names)
    # value is list of ventures names (in group)
    for group_name, ventures in virtual_venture_names.items():
        usage_names = {
            'virtual_cores': '{0} Virtual CPU cores'.format(group_name),
            'virtual_memory': '{0} Virtual memory MB'.format(group_name),
            'virtual_disk': '{0} Virtual disk MB'.format(group_name),
        }
        usages = get_or_create_usages(usage_names)
        for venture_name in ventures:
            counter = 0
            for data in api_pricing.get_virtual_usages(venture_name):
                update(data, usages, date)
                counter += 1
            logger.info('Venture {0} done - {1} devices processed'.format(
                venture_name,
                counter,
            ))
    return True, 'virtual usages updated', kwargs

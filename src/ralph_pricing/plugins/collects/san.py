# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin, api_pricing
from ralph_pricing.models import UsageType, DailyUsage, Device, DailyDevice

logger = logging.getLogger(__name__)


def update_usage(device, venture, date, value, usage_type):
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
    )
    usage.pricing_venture = venture
    usage.value = value
    usage.save()


def update(data, date, usage_type):
    try:
        device = Device.objects.get(
            device_id=data['device_id'],
        )
    except Device.DoesNotExist:
        logger.warning(
            'Device {} not found in Scrooge'.format(data['device_id'])
        )
        return False

    venture = None
    try:
        daily_device = device.dailydevice_set.get(date=date)
        venture = daily_device.pricing_venture
    except DailyDevice.DoesNotExist:
        logger.warning('DailyDevice for id {} and date {} not found'.format(
            data['device_id'],
            date,
        ))
        return False
    if venture is None:
        logger.error(
            'Venture not specified for DailyDevice {} and date {}'.format(
                data['device_id'],
                date,
            )
        )
        return False
    update_usage(device, venture, date, 1, usage_type)
    return True


def get_usage_type():
    return UsageType.objects.get_or_create(
        symbol='san',
        defaults=dict(
            name='SAN',
        )
    )


@plugin.register(chain='pricing', requires=['assets'])
def san(**kwargs):
    """Updates the SAN usages from Ralph."""
    usage_type, created = get_usage_type()
    date = kwargs['today']
    results = [update(d, date, usage_type) for d in api_pricing.get_fc_cards()]
    return (
        True,
        'SAN usages updated:{} (total: {})'.format(sum(results), len(results)),
        kwargs
    )

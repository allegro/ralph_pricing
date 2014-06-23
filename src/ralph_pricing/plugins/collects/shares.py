# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin, api_pricing
from ralph_pricing.models import (
    DailyDevice,
    DailyUsage,
    Device,
    UsageType,
    Venture,
)


logger = logging.getLogger(__name__)


def update_usage(device, venture, usage_type, date, value):
    """
    Saves single DailyUsage of shares usage type.
    """
    if not value:
        return
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
        pricing_venture=venture,
    )
    usage.value += value
    usage.save()


def update(data, date, usage_type, unknown_venture=None):
    """
    Updates single record according to information in data.
    """
    device_id = data['mount_device_id']
    if device_id is None:
        return False
    venture = None
    device = None
    try:
        device = Device.objects.get(
            device_id=device_id,
        )
        daily_device = device.dailydevice_set.get(date=date)
        venture = daily_device.pricing_venture
    except Device.DoesNotExist:
        logger.warning('Device {} not found'.format(device_id))
    except DailyDevice.DoesNotExist:
        logger.warning('Daily Device {} not found'.format(device_id))

    # if venture is None, check if unknown venture was defined
    if venture is None:
        if unknown_venture is not None:
            venture = unknown_venture
        else:
            return False
    update_usage(device, venture, usage_type, date, data['size'])
    return True


def get_or_create_usage_type(usage_name):
    """
    Returns usage type for specific shares
    """
    usage_type, created = UsageType.objects.get_or_create(
        symbol=usage_name.replace(' ', '_').lower(),
        defaults=dict(
            name=usage_name,
            average=True,
        ),
    )
    return usage_type


@plugin.register(chain='pricing', requires=['assets', 'virtual'])
def shares(**kwargs):
    """Updates the disk share usages from Ralph."""

    date = kwargs['today']
    shares_venture_symbols = settings.SHARE_VENTURE_SYMBOLS

    unknown_venture = None
    try:
        unknown_venture = Venture.objects.get(
            symbol=settings.SHARES_UNKNOWN_VENTURE
        )
    except AttributeError:
        logger.warning('Shares unknown venture not configured')
    except Venture.DoesNotExist:
        logger.error('Shares unknown venture ({}) not found'.format(
            settings.SHARES_UNKNOWN_VENTURE
        ))

    for group_name, ventures in shares_venture_symbols.iteritems():
        usage_name = 'Disk Shares {0}'.format(group_name)
        usage_type = get_or_create_usage_type(usage_name)

        logger.info('Processing group {}'.format(group_name))

        # delete all previous records
        DailyUsage.objects.filter(type=usage_type, date=date).delete()

        for venture_symbol in ventures:
            counter = 0
            saved = 0
            for data in api_pricing.get_shares(
                venture_symbol=venture_symbol,
                include_virtual=False,
            ):
                if update(data, date, usage_type, unknown_venture):
                    saved += 1
                counter += 1
            logger.info(
                '{0} (total: {1}) share mounts from venture {2} saved'.format(
                    saved,
                    counter,
                    venture_symbol,
                )
            )
    return True, 'disk share usages updated', kwargs

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph_pricing.models import DailyUsage, DailyDevice, UsageType, Venture


logger = logging.getLogger(__name__)


class VentureNotDefinedError(Exception):
    '''
        Exception raised when device have no defined any venture symbol
    '''
    pass


class DefinedVentureDoesNotExist(Exception):
    '''
        Exception raised when there is no venture for the defined symbol
    '''
    pass


def set_usages(daily_device, date):
    '''
        Create daily usage for single device

        :param object device: device from which the report will be generated
        :param datetime date: Date from which the report will be generated
        :returns boolean: Information for counting true/false processed devices
        :rtype boolean:
    '''
    usage_type, created = UsageType.objects.get_or_create(
        name='Power consumption',
        by_warehouse=True,
        by_cost=True,
    )

    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_venture=daily_device.pricing_venture,
        warehouse=daily_device.warehouse,
    )

    usage.value += daily_device.power_consumption
    usage.save()

    return True


@plugin.register(chain='pricing', requires=['assets'])
def powerconsumption(**kwargs):
    '''
        Create daily usage imprint of power consumption.

        :param datetime today: Date from which the report will be generated
        :returns tuple: result status and message
    '''
    if 'today' not in kwargs:
        return False, 'Not configured.', kwargs

    count = 0
    for device in DailyDevice.objects.filter(date=kwargs['today']):
        try:
            count += set_usages(device, kwargs['today'])
        except DefinedVentureDoesNotExist:
            logger.error('Venture does not exist')
        except VentureNotDefinedError:
            logger.error(
                'Venture: device have no any information about venture'
            )

    return (
        True,
        'Creation a daily imprint of power consumption for date {0}'
        ' completed! Processed {1} devices'.format(kwargs['today'], count),
        kwargs
    )

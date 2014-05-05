# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin
from ralph.util.api_pricing import get_cloud_daily_costs
from ralph_pricing.models import (
    Venture,
    DailyUsage,
    UsageType,
)


logger = logging.getLogger(__name__)


def set_cloud_daily_costs(data, date, usage_type):
    """
    Updates single cloud daily cost.

    Because of getting cloud cost per venture from Ralph, cloud usage has
    regular type and it's price should be set to 1, so cost in scrooge will
    match cost from ralph (regular usage type is only a proxy to show cloud
    cost on scrooge report).
    """
    try:
        venture = Venture.objects.get(venture_id=data['venture_id'])
    except Venture.DoesNotExist:
        logger.warning(
            'Venture with id {} does not exist'.format(data['venture_id'])
        )
        if settings.CLOUD_UNKNOWN_VENTURE:
            try:
                venture = Venture.objects.get(
                    symbol=settings.CLOUD_UNKNOWN_VENTURE
                )
                logger.warning('Using {} venture instead'.format(
                    settings.CLOUD_UNKNOWN_VENTURE
                ))
            except Venture.DoesNotExist:
                return False
        else:
            return False

    daily_usage, created = DailyUsage.objects.get_or_create(
        type=usage_type,
        date=date,
        pricing_venture=venture,
    )
    daily_usage.value = data['daily_cost']
    daily_usage.save()
    return created


def get_cloud_usage():
    """Creates cloud usage type if not created."""
    usage_type, created = UsageType.objects.get_or_create(
        symbol='cloud',
        defaults=dict(
            name='Cloud',
            type='RU',
        )
    )
    return usage_type


@plugin.register(chain='pricing', requires=['ventures'])
def cloud(**kwargs):
    """Updates the cloud usages (costs) from Ralph."""
    date = kwargs['today']
    cloud_usage_type = get_cloud_usage()
    count = sum(
        set_cloud_daily_costs(data, date, cloud_usage_type)
        for data in get_cloud_daily_costs(date)
    )
    return True, '%d new cloud daily costs added' % count, kwargs

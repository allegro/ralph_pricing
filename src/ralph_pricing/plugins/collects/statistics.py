# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph_pricing.models import UsageType, DailyStatistics, DailyUsage


logger = logging.getLogger(__name__)


def create_statistic_imprint(usage, date):
    statistic = DailyStatistics.objects.get_or_create(
        date=date,
        type=usage,
    )[0]
    statistic.count = DailyUsage.objects.filter(
        date=date,
        type=usage,
    ).count()
    statistic.save()


# virtual usages requires assets plugin to get proper devices
@plugin.register(chain='pricing')
def statistics(**kwargs):
    """Updates the virtual usages from Ralph."""

    date = kwargs['today']
    for usage in UsageType.objects.all():
        create_statistic_imprint(usage, date)
    return True, 'virtual usages updated', kwargs

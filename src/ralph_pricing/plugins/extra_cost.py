# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

from ralph.util import plugin, api_pricing
from ralph_pricing.models import DailyUsage, UsageType, Venture, UsagePrice


def update_extra_cost(data, date):
    usage_type, created = UsageType.objects.get_or_create(
        name=data['type'],
    )
    venture, created = Venture.objects.get_or_create(
        venture_id=data['venture_id'],
    )
    if created:
        venture.name = data['venture']
        venture.save()
    daily, daily_created = DailyUsage.objects.get_or_create(
        pricing_venture=venture,
        date=date,
        type=usage_type,
    )
    try:
        price, created = UsagePrice.objects.get_or_create(
            type=usage_type,
            price=data['cost'],
            start=data['start'],
            end=data['end'] if data['end'] else datetime.date(2048, 10, 24),
        )
    except:
        import pdb; pdb.set_trace()
    return daily_created


@plugin.register(chain='pricing', requires=[])
def extra_cost(**kwargs):

    date = kwargs['today']
    count = sum(
        update_extra_cost(data, date) for data in api_pricing.get_extra_cost()
    )
    return True, '%d exitacost' % count, kwargs

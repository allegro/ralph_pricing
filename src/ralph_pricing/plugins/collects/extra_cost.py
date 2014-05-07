# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import decimal
from calendar import monthrange

from ralph.util import plugin, api_pricing
from ralph_pricing.models import ExtraCost, Venture, DailyExtraCost


def update_extra_cost(data, date):
    cost_type, created = DailyExtraCost.objects.get_or_create(
        date=date,
        pricing_venture=data.pricing_venture,
        type=data.type,
        defaults=dict(
            value=data.price/monthrange(date.year, date.month)[1],
        )
    )
    return created


@plugin.register(chain='pricing', requires=['ventures'])
def extracost(**kwargs):
    date = kwargs['today']
    count = sum(
        (
            update_extra_cost(data, date)
            for data in ExtraCost.objects.all()
        )
    )
    return True, '%d new extracosts' % count, kwargs

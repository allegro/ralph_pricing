# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from calendar import monthrange

from ralph.util import plugin
from ralph_pricing.models import ExtraCost, DailyExtraCost


def update_extra_cost(data, date):
    """
    Create daily imprint from given data.

    :param datetime date: Date for which imprint will be created
    :param dict data: Dict with data from ExtraCost.
    :returns boolean: Information about succest get/create imprints
    :rtype:
    """
    daily_extra_cost, created = DailyExtraCost.objects.get_or_create(
        date=date,
        pricing_venture=data.pricing_venture,
        type=data.type,
    )
    daily_extra_cost.value = (
        data.monthly_cost/monthrange(date.year, date.month)[1]
    )
    daily_extra_cost.save()
    return created


@plugin.register(chain='pricing', requires=['ventures'])
def extracost(**kwargs):
    """
    Main method of daily imprint create.
    """
    date = kwargs['today']
    count = sum(
        (
            update_extra_cost(data, date)
            for data in ExtraCost.objects.all()
        )
    )
    return True, '%d new extracosts' % count, kwargs

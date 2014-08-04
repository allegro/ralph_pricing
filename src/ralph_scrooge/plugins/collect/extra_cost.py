# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from calendar import monthrange

from ralph.util import plugin
from ralph_scrooge.models import ExtraCost, DailyExtraCost, ExtraCostChoices


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
        service=data.service,
        type=data.type,
    )
    daily_extra_cost.value = (
        data.monthly_cost/monthrange(date.year, date.month)[1]
    )
    daily_extra_cost.save()
    return created


@plugin.register(chain='scrooge', requires=[])
def extra_cost(**kwargs):
    """
    Main method of daily imprint create.
    """
    date = kwargs['today']
    new = total = 0
    for data in ExtraCost.objects.filter(mode=ExtraCostChoices.daily_imprint):
        if update_extra_cost(data, date):
            new += 1
        total += 1
    return True, '{0} new, {1} updated, {2} total'.format(
        new,
        total-new,
        total,
    )

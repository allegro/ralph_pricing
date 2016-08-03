# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin  # XXX to be replaced later..?
from ralph_scrooge.models import BusinessLine, ProfitCenter
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


@commit_on_success
def update_profit_center(pc, default_business_line):
    if pc['business_segment'] is not None:
        business_line = BusinessLine.objects.get(
            ci_id=pc['business_segment']['id']
        )
    else:
        business_line = default_business_line
    profit_center, created = ProfitCenter.objects.get_or_create(
        ci_id=pc['id'],
    )
    profit_center.name = pc['name']
    profit_center.description = pc['description']
    profit_center.business_line = business_line
    profit_center.save()
    return created


@plugin.register(chain='scrooge', requires=['business_line'])
def profit_center(**kwargs):
    new_pc = total = 0
    default_business_line = BusinessLine.objects.get(pk=1)
    for pc in get_from_ralph("profit-centers", logger):
        created = update_profit_center(pc, default_business_line)
        if created:
            new_pc += 1
        total += 1
    return True, '{} new profit center(s), {} updated, {} total'.format(
        new_pc,
        total - new_pc,
        total,
    )

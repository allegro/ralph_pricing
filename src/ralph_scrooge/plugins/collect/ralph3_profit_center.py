# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

# TODO(xor-xor): To be eventually replaced by some other plugin mechanism,
# which won't be tied to Ralph.
from ralph.util import plugin
# TODO(xor-xor): BusinessLine should be renamed to BusinessSegment (this also
# applies to other occurrences of this name in this plugin).
from ralph_scrooge.models import BusinessLine, ProfitCenter
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


@commit_on_success
def update_profit_center(pc, default_business_line):
    if pc['business_segment'] is not None:
        business_line = BusinessLine.objects.get(
            ralph3_id=pc['business_segment']['id']
        )
    else:
        business_line = default_business_line
    profit_center, created = ProfitCenter.objects.get_or_create(
        ralph3_id=pc['id'],
        defaults=dict(
            name=pc['name'],
        )
    )
    profit_center.name = pc['name']
    profit_center.description = pc['description']
    profit_center.business_line = business_line
    profit_center.save()
    return created


@plugin.register(chain='scrooge', requires=['business_segment'])
def ralph3_profit_center(**kwargs):
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

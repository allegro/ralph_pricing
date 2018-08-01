# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db import transaction

from ralph_scrooge.models import ProfitCenter
from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


@transaction.atomic
def update_profit_center(pc):
    profit_center, created = ProfitCenter.objects.get_or_create(
        ralph3_id=pc['id'],
        defaults=dict(
            name=pc['name'],
        )
    )
    profit_center.name = pc['name']
    profit_center.description = pc['description']
    profit_center.save()
    return created


@plugin_runner.register(chain='scrooge')
def ralph3_profit_center(**kwargs):
    new_pc = total = 0
    for pc in get_from_ralph("profit-centers", logger):
        created = update_profit_center(pc)
        if created:
            new_pc += 1
        total += 1
    return True, '{} new profit center(s), {} updated, {} total'.format(
        new_pc,
        total - new_pc,
        total,
    )

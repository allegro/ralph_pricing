# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin  # XXX to be replaced later..?
from ralph_scrooge.models import BusinessLine  # XXX what about renaming this to BusinessSegment, as in Ralph3 API..?
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


@commit_on_success
def update_business_line(bl):
    business_line, created = BusinessLine.objects.get_or_create(
        ci_id=bl['id'],
    )
    business_line.name = bl['name']
    business_line.save()
    return created


@plugin.register(chain='scrooge', requires=[])
def business_line(**kwargs):
    new_bl = total = 0
    for bl in get_from_ralph("business-segments", logger):
        created = update_business_line(bl)
        if created:
            new_bl += 1
        total += 1
    return True, '{} new business line(s), {} updated, {} total'.format(
        new_bl,
        total - new_bl,
        total,
    )

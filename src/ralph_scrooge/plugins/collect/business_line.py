# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph.util.api_scrooge import get_business_lines
from ralph_scrooge.models import BusinessLine


logger = logging.getLogger(__name__)


@commit_on_success
def update_business_line(data, date):
    business_line, created = BusinessLine.objects.get_or_create(
        ci_id=data['ci_id'],
    )
    business_line.ci_uid = data['ci_uid']
    business_line.name = data['name']
    business_line.save()
    return created


@plugin.register(chain='scrooge', requires=[])
def business_line(today, **kwargs):
    """
    Updates Business Lines from CMDB
    """
    new_bl = total = 0
    for data in get_business_lines():
        if update_business_line(data, today):
            new_bl += 1
        total += 1
    return True, '{} new business line(s), {} updated, {} total'.format(
        new_bl,
        total - new_bl,
        total,
    )

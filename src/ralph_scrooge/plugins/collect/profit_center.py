# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph.util.api_scrooge import get_profit_centers
from ralph_scrooge.models import BusinessLine, ProfitCenter


logger = logging.getLogger(__name__)


@commit_on_success
def update_profit_center(data, date, default_business_line):
    """
    Updates single profit center according to data from ralph
    """
    if data['business_line'] is not None:
        business_line = BusinessLine.objects.get(ci_id=data['business_line'])
    else:
        business_line = default_business_line
    profit_center, created = ProfitCenter.objects.get_or_create(
        ci_id=data['ci_id'],
    )
    profit_center.ci_uid = data['ci_uid']
    profit_center.name = data['name']
    profit_center.description = data['description']
    profit_center.business_line = business_line
    profit_center.save()
    return created


@plugin.register(chain='scrooge', requires=['business_line'])
def profit_center(today, **kwargs):
    """
    Updates Business Lines from CMDB
    """
    new_bl = total = 0
    default_business_line = BusinessLine.objects.get(pk=1)
    for data in get_profit_centers():
        if update_profit_center(data, today, default_business_line):
            new_bl += 1
        total += 1
    return True, '{} new profit center(s), {} updated, {} total'.format(
        new_bl,
        total - new_bl,
        total,
    )

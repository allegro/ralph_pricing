# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph.util.api_scrooge import get_environments
from ralph_scrooge.models import Environment


logger = logging.getLogger(__name__)


@commit_on_success
def update_environment(data, date):
    environment, created = Environment.objects.get_or_create(
        ci_id=data['ci_id'],
    )
    environment.ci_uid = data['ci_uid']
    environment.name = data['name']
    environment.save()
    return created


@plugin.register(chain='scrooge', requires=[])
def environment(today, **kwargs):
    """
    Updates Environments from Ralph
    """
    new_bl = total = 0
    for data in get_environments():
        if update_environment(data, today):
            new_bl += 1
        total += 1
    return True, '{} new environment(s), {} updated, {} total'.format(
        new_bl,
        total - new_bl,
        total,
    )

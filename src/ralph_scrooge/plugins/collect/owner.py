# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph.util.api_pricing import get_owners
from ralph_scrooge.models import Owner


logger = logging.getLogger(__name__)


@commit_on_success
def update_owner(data, date):
    owner, created = Owner.objects.get_or_create(
        cmdb_id=data['id']
    )
    owner.first_name = data['first_name']
    owner.last_name = data['last_name']
    owner.email = data['email']
    owner.sAMAccountName = data['sAMAccountName']
    owner.save()
    return created


@plugin.register(chain='scrooge', requires=[])
def owner(today, **kwargs):
    """
    Updates Owners from CMDB
    """
    new_owners = total = 0
    for data in get_owners():
        if update_owner(data, today):
            new_owners += 1
        total += 1
    return True, '{} new owner(s), {} updated, {} total'.format(
        new_owners,
        total - new_owners,
        total,
    )

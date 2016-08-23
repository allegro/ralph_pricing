# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

# TODO(xor-xor): To be eventually replaced by some other plugin mechanism,
# which won't be tied to Ralph.
from ralph.util import plugin
# TODO(xor-xor): Warehouse should be renamed to DataCenter (this also
# applies to other occurrences of this name in this plugin).
from ralph_scrooge.models import Warehouse
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


def update_data_centers(dc_from_ralph):
    warehouse, created = Warehouse.objects.get_or_create(
        ralph3_id=dc_from_ralph['id']
    )
    warehouse.name = dc_from_ralph['name']
    warehouse.save()
    return created


@plugin.register(chain='scrooge')
def data_center(**kwargs):
    new = total = 0
    for dc in get_from_ralph("data-centers", logger):
        total += 1
        created = update_data_centers(dc)
        if created:
            new += 1

    return True, '{} new data centers, {} updated, {} total'.format(
        new,
        total - new,
        total,
    )

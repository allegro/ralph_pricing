# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph_assets.api_scrooge import get_warehouses
from ralph_scrooge.models import Warehouse


logger = logging.getLogger(__name__)


def update_warehouses(data):
    """
    Update information about warehouses

    :param dict data: dict with information about single warehouse
    :returns boolean: True, if warehouse was created
    :rtype boolean:
    """
    warehouse, created = Warehouse.objects.get_or_create(
        id_from_assets=data['warehouse_id']
    )
    warehouse.name = data['warehouse_name']
    warehouse.save()
    return created


@plugin.register(chain='scrooge')
def warehouse(**kwargs):
    """
    Get all information about warehouses

    :returns tuple: result status, message
    """
    new = total = 0
    for warehouse in get_warehouses():
        total += 1
        if update_warehouses(warehouse):
            new += 1

    return True, 'Warehouses: {0} new, {1} updated, {2} total'.format(
        new,
        total-new,
        total,
    )

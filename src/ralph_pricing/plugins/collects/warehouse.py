# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph_assets.api_pricing import get_warehouses
from ralph_pricing.models import Warehouse


logger = logging.getLogger(__name__)


def update_warehouses(data):
    '''
        Update information about warehouses

        :param dict data: dict with information about single warehouse
        :returns boolean: Information for counting true processed warehouses
        :rtype boolean:
    '''
    warehouse = Warehouse.objects.get_or_create(id=data['warehouse_id'])[0]
    warehouse.name = data['warehouse_name']
    warehouse.save()
    return True


@plugin.register(chain='pricing')
def warehouse(**kwargs):
    '''
        Get all information about warehouses

        :returns tuple: result status, message and kwargs
    '''

    count = sum(update_warehouses(data) for data in get_warehouses())

    return (True, 'Got {0} warehouses'.format(count), kwargs)

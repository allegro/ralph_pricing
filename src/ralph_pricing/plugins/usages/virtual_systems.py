# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin


logger = logging.getLogger(__name__)


@plugin.register(chain='usages')
def virtual_systems_usages(**kwargs):
    logger.debug("Get virtual systems usage")
    usages = {}
    for venture in kwargs.get('ventures'):
        usages[venture.id] = {
            'virtual_disk_count': 7.1,
            'virtual_disk_cost': 0.71,
            'virtual_memory_count': 7.2,
            'virtual_memory_cost': 0.72,
            'virtual_cpu_cores_count': 7.3,
            'virtual_cpu_cores_cost': 0.73,
            'virtual_schema_cost': 2.16,
        }
    return usages


@plugin.register(chain='usages')
def virtual_systems_schema(**kwargs):
    logger.debug("Get virtual systems schema")
    schema = OrderedDict()
    schema['virtual_disk_count'] = {
        'name': _("Virtual disk MB count"),
    }
    schema['virtual_disk_cost'] = {
        'name': _("Virtual disk MB cost"),
        'currency': True,
    }
    schema['virtual_memory_count'] = {
        'name': _("Virtual memory MB count"),
    }
    schema['virtual_memory_cost'] = {
        'name': _("Virtual memory MB cost"),
        'currency': True,
    }
    schema['virtual_cpu_cores_count'] = {
        'name': _("Virtual CPU cores count"),
    }
    schema['virtual_cpu_cores_cost'] = {
        'name': _("Virtual CPU cores cost"),
        'currency': True,
    }
    schema['virtual_schema_cost'] = {
        'name': _("Virtual systems cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

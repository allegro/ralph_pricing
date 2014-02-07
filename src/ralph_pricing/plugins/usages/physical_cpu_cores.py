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
def physical_cpu_cores_usages(**kwargs):
    logger.debug("Get phisical cpu cores usage")
    usages = {}
    for venture in kwargs.get('ventures'):
        usages[venture.id] = {
            'physical_cpu_cores_count': 4,
            'physical_cpu_cores_cost': 0.4,
        }
    return usages


@plugin.register(chain='usages')
def physical_cpu_cores_schema(**kwargs):
    logger.debug("Get phisical cpu cores schema")
    schema = OrderedDict()
    schema['physical_cpu_cores_count'] = {
        'name': _("Physical cpu cores count"),
    }
    schema['physical_cpu_cores_cost'] = {
        'name': _("Physical cpu cores cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

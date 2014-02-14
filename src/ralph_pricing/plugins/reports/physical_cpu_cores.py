# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict

from django.utils.translation import ugettext_lazy as _

from ralph_pricing.models import UsageType
from ralph.util import plugin
from ralph_pricing.plugins.reports.utils import get_standard_usages_and_costs


logger = logging.getLogger(__name__)


@plugin.register(chain='reports')
def physical_cpu_cores_usages(**kwargs):
    logger.debug("Get phisical cpu cores usage")
    usage_type = UsageType.objects.get(name='physical_cpu_cores')
    core_usages = get_standard_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )

    usages = defaultdict(lambda: defaultdict(int))
    for venture, core_usage in core_usages.iteritems():
        usages[venture]['physical_cpu_cores_count'] = core_usage['value']
        usages[venture]['physical_cpu_cores_cost'] = core_usage['cost']

    return usages


@plugin.register(chain='reports')
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

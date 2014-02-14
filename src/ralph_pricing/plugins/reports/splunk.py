# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import OrderedDict, defaultdict

from django.utils.translation import ugettext_lazy as _

from ralph.util import plugin
from ralph_pricing.models import UsageType
from ralph_pricing.plugins.reports.utils import get_standard_usages_and_costs


logger = logging.getLogger(__name__)


@plugin.register(chain='reports')
def splunk_usages(**kwargs):
    logger.debug("Splunk usage")
    usage_type = UsageType.objects.get(name='splunk')
    splunk_usages = get_standard_usages_and_costs(
        kwargs['start'],
        kwargs['end'],
        kwargs['ventures'],
        usage_type,
    )

    usages = defaultdict(lambda: defaultdict(int))
    for venture, splunk_usage in splunk_usages.iteritems():
        usages[venture]['splunk_usage_count'] = splunk_usage['value']
        usages[venture]['splunk_usage_cost'] = splunk_usage['cost']

    return usages


@plugin.register(chain='reports')
def splunk_schema(**kwargs):
    logger.debug("Splunk usage schema")
    schema = OrderedDict()
    schema['splunk_usage_count'] = {
        'name': _("Splunk usage count"),
    }
    schema['splunk_usage_cost'] = {
        'name': _("Splunk usage cost"),
        'currency': True,
        'total_cost': True,
    }
    return schema

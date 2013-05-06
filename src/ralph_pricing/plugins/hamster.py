# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import urllib

from django.conf import settings
from restkit import Resource, ResourceNotFound

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage


logger = logging.getLogger(__name__)


def update_hamster_usage(venture, usage_type, date, url):
    venture_symbol = venture.symbol
    try:
        capacity = get_venture_capacity(venture_symbol, url)
    except ResourceNotFound:
        # apache not found error
        logger.error('Hamster data for %s not found' % venture_symbol)
    if capacity:
        return set_hamster_usage(venture, capacity, usage_type, date)
    return False


def get_venture_capacity(venture_symbol, url):
    resource = Resource(url)
    ret = resource.get(urllib.quote_plus(venture_symbol.encode('utf-8')))
    json_data = json.loads(ret.body_string())
    return json_data.get('capacity')


def set_hamster_usage(venture, capacity, usage_type, date):
    usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_venture=venture,
    )
    usage.value = capacity
    usage.save()
    return created


@plugin.register(chain='pricing', requires=['sync_ventures'])
def hamster_usage(**kwargs):
    """Updates the Hamster usage from Ralph."""
    if not settings.HAMSTER_API_URL:
        return False, "Not configured", {}
    url = settings.HAMSTER_API_URL
    usage_type, created = UsageType.objects.get_or_create(
        name="Hamster Capacity 1 GB",
    )
    date = kwargs['today']
    ventures = Venture.objects.filter(symbol__gt='')
    count = sum(
        update_hamster_usage(venture, usage_type, date, url)
        for venture in ventures
    )
    return True, '%d Ventures ???' % count, kwargs

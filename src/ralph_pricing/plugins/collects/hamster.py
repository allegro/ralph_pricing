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
        logger.error('Hamster data for %r not found' % venture_symbol)
    else:
        if capacity > 0:
            return set_hamster_usage(venture, capacity, usage_type, date)


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
    usage.value = capacity / (1024 * 1024)  # in MB
    usage.save()
    return created


@plugin.register(chain='pricing', requires=['ventures'])
def hamster(**kwargs):
    """Updates Hamster usage per Venture"""
    if not settings.HAMSTER_API_URL:
        return False, "Not configured", kwargs
    url = settings.HAMSTER_API_URL
    usage_type, created = UsageType.objects.get_or_create(
        name="Hamster Capacity 1 MB",
    )
    date = kwargs['today']
    ventures = Venture.objects.all()
    count = sum(
        update_hamster_usage(venture, usage_type, date, url) or 0
        for venture in ventures
    )
    return True, '%d new Hamster usage added in Ventures' % count, kwargs

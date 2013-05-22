#!/usr/bin/env python
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
from ralph_pricing.models import DailyUsage, UsageType, Venture


logger = logging.getLogger(__name__)


def get_ventures_capacities(date, url):
    resource = Resource(url)
    ret = resource.get(urllib.quote_plus(date.strftime("%Y-%m-%d")))
    json_data = json.loads(ret.body_string())
    return json_data


def update_scaleme_usage(usage_types, date, url):
    try:
        ventures_capacity = get_ventures_capacities(date, url)
    except ResourceNotFound:
        # apache not found error
        logger.error('Scaleme data for %r date not found' % date)
    else:
        for venture_symbol, venture_usages in ventures_capacity.iteritems():
            try:
                venture = Venture.objects.get(symbol=venture_symbol)
            except Venture.DoesNotExist:
                pass
            else:
                for usage_name, usage_type in usage_types.iteritems():
                    usage, created = DailyUsage.objects.get_or_create(
                        date=date,
                        type=usage_type,
                        pricing_venture=venture,
                    )
                    usage.value = venture_usages[usage_name]
                    usage.save()


@plugin.register(chain='pricing', requires=['ventures'])
def scaleme(**kwargs):
    """ Update Scaleme usage per Venture """
    if not settings.SCALEME_API_URL:
        return False, "Not configured.", kwargs
    url = settings.SCALEME_API_URL
    usage_type_backend, created = UsageType.objects.get_or_create(
        name='Scaleme transforming image 1 event',
    )
    usage_type_cache, created = UsageType.objects.get_or_create(
        name='Scaleme image from cache 1 event',
    )
    usage_types = {
        'cache': usage_type_cache,
        'backend': usage_type_backend,
    }
    date = kwargs['today']
    update_scaleme_usage(usage_types, date, url)
    return True, 'Scaleme usages added to Ventures', kwargs

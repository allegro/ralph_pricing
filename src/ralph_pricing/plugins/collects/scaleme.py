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
        message = 'Scaleme data for %r not found' % date.strftime("%Y-%m-%d")
        logger.error(message)
    else:
        if ventures_capacity:
            counts = {'new': 0, 'updated': 0}
            for venture_symbol, venture_usages in ventures_capacity.iteritems():  # noqa
                try:
                    venture = Venture.objects.get(symbol=venture_symbol)
                except Venture.DoesNotExist:
                    logger.warning(
                        'Venture with venture symbol "{0}" does not'
                        ' exist'.format(venture_symbol)
                    )
                else:
                    for usage_name, usage_type in usage_types.iteritems():
                        usage, created = DailyUsage.objects.get_or_create(
                            date=date,
                            type=usage_type,
                            pricing_venture=venture,
                        )
                        usage.value = venture_usages[usage_name]
                        usage.save()
                        if created:
                            counts['new'] += 1
                        else:
                            counts['updated'] += 1
            message = 'Scaleme ussages in Ventures: {} new, {} updated'.format(
                counts['new'], counts['updated']
            )
        else:
            message = 'Scaleme data for %r not found' % date.strftime(
                "%Y-%m-%d"
            )
    return message


@plugin.register(chain='pricing', requires=['ventures'])
def scaleme(**kwargs):
    """ Update Scaleme usage per Venture """
    if not settings.SCALEME_API_URL:
        return False, "Not configured.", kwargs
    url = settings.SCALEME_API_URL
    usage_type_backend, created = UsageType.objects.get_or_create(
        name='Scaleme transforming an image 10000 events',
    )
    usage_type_cache, created = UsageType.objects.get_or_create(
        name='Scaleme serving image from cache 10000 events',
    )
    usage_types = {
        'cache': usage_type_cache,
        'backend': usage_type_backend,
    }
    date = kwargs['today']
    message = update_scaleme_usage(usage_types, date, url)
    return True, message, kwargs

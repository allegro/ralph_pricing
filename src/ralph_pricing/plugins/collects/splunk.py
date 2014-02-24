# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import time
import logging

from django.conf import settings

from ralph.util import plugin
from ralph.util.api_pricing import get_device_by_name
from ralph_pricing.splunk import Splunk
from ralph_pricing.models import (
    DailyUsage,
    Device,
    UsageType,
    Venture,
)

logger = logging.getLogger(__name__)


class VentureIdNone(Exception):
    pass


def set_usages(date, usage, usage_type, host, splunk_venture):
    device_info = get_device_by_name(host)
    device_id = device_info.get('device_id')
    venture_id = device_info.get('venture_id')

    if device_id is None:
        logger.warning('Device with host %s not found in ralph', host)

    # device
    try:
        device = device_id and Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        device = None

    # venture
    try:
        if venture_id is None:
            raise VentureIdNone()
        venture = Venture.objects.get(venture_id=venture_id)
    except (VentureIdNone, Venture.DoesNotExist):
        logger.warning(
            'Device with host %s attached to splunk unknown venture', host)
        venture = splunk_venture

    # save device information if found in pricing
    if device is not None:
        daily_usage, created = DailyUsage.objects.get_or_create(
            date=date,
            type=usage_type,
            pricing_device=device,
            pricing_venture=venture,
        )
        daily_usage.remarks = host
    else:
        # if device not found in pricing, try to find DailyUsage by adding
        # remarks as filter - in case of DailyUsage, remark should always be
        # hostname (grouping by hostname in main plugin)
        daily_usage, created = DailyUsage.objects.get_or_create(
            date=date,
            type=usage_type,
            pricing_venture=venture,
            remarks=host,
        )
    daily_usage.value = usage
    daily_usage.save()


@plugin.register(chain='pricing', requires=['ventures', 'assets'])
def splunk(**kwargs):
    """Updates Splunk usage per Venture"""
    if not settings.SPLUNK_HOST:
        return False, "Not configured.", kwargs
    try:
        splunk_venture = Venture.objects.get(symbol='splunk_unknown_usage')
    except Venture.DoesNotExist:
        return False, 'Splunk venture does not exist!', kwargs
    usage_type, created = UsageType.objects.get_or_create(
        name="Splunk Volume 1 MB",
    )
    date = kwargs['today']
    splunk = Splunk()
    days_ago = (date - datetime.date.today()).days
    earliest = '{}d@d'.format(days_ago - 1)
    latest = '{}d@d'.format(days_ago) if days_ago != 0 else 'now'
    splunk.start(earliest=earliest, latest=latest)
    percent = splunk.progress
    while percent < 100:
        print(percent)
        time.sleep(30)
        percent = splunk.progress
    hosts = {}
    for item in splunk.results:
        host = item['host']
        mb = float(item['MBytes'])
        if host in hosts:
            hosts[host] += mb
        else:
            hosts[host] = mb
    for host, usage in hosts.iteritems():
        set_usages(date, usage, usage_type, host, splunk_venture)
    return True, 'done.', kwargs

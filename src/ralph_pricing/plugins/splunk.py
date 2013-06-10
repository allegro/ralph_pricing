# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import time

from django.conf import settings

from ralph.util import plugin
from ralph_pricing.splunk import Splunk
from ralph_pricing.models import (
    DailyDevice,
    DailyUsage,
    Device,
    SplunkName,
    UsageType,
    Venture,
)


def set_device_usage(date, usage, usage_type, device):
    try:
        daily_device = DailyDevice.objects.get(
            pricing_device=device,
            date=date,
        )
    except DailyDevice.DoesNotExist:
        venture = None
    else:
        venture = daily_device.pricing_venture
    daily_usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
        pricing_venture=venture,
    )
    daily_usage.value = usage
    daily_usage.save()


def set_unknown_usage(date, usage, usage_type, splunk_venture):
    daily_usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_venture=splunk_venture,
        value=usage,
    )


def set_usages(date, usage, usage_type, host, splunk_venture):
    try:
        splunk_pair = SplunkName.objects.get(
            splunk_name=host,
            pricing_device__name=host,
        )
    except SplunkName.DoesNotExist:
        try:
            splunk_pair = SplunkName.objects.get(
                splunk_name=host,
                pricing_device__isnull=False,
            )
        except SplunkName.DoesNotExist:
            device = Device.objects.filter(name=host)
            if device:
                splunk_pair = SplunkName(
                    splunk_name=host,
                    pricing_device=device[0],
                )
                splunk_pair.save()
                set_device_usage(date, usage, usage_type, device[0])
            else:
                SplunkName.objects.get_or_create(splunk_name=host)
                set_unknown_usage(date, usage, usage_type, splunk_venture)
        else:
            set_device_usage(
                date, usage, usage_type, splunk_pair.pricing_device,
            )
    else:
        set_device_usage(date, usage, usage_type, splunk_pair.pricing_device)


@plugin.register(chain='pricing', requires=['ventures', 'devices'])
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

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
    daily_device = DailyDevice.objects.get(pricing_device=device)
    daily_usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_device=device,
        pricing_venture=daily_device.pricing_venture
    )
    daily_usage.value = usage
    daily_usage.save()


def set_unknown_usage(date, usage, usage_type, splunk_venture):
    daily_usage, created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        pricing_venture=splunk_venture,
        value=usage
    )


def set_usages(date, usage, usage_type, host, splunk_venture):
    try:
        splunk_pair = SplunkName.objects.get(
            splunk_name=host,
            pricing_device__name=host
        )
    except SplunkName.DoesNotExist:
        try:
            splunk_pair = SplunkName.objects.get(
                splunk_name=host,
                pricing_device__isnull=False
            )
        except SplunkName.DoesNotExist:
            device = Device.objects.filter(name=host)
            if device:
                splunk_pair = SplunkName(
                    splunk_name=host,
                    pricing_device=device[0]
                )
                splunk_pair.save()
                set_device_usage(date, usage, usage_type, device[0])
            else:
                SplunkName(splunk_name=host).save()
                set_unknown_usage(date, usage, usage_type, splunk_venture)
        else:
            set_device_usage(date, usage, usage_type, splunk_pair.pricing_device)
    else:
        set_device_usage(date, usage, usage_type, splunk_pair.pricing_device)


@plugin.register(chain='pricing', requires=['sync_ventures', 'sync_devices'])
def splunk(**kwargs):
    """Updates Splunk usage per Venture"""
    if not settings.SPLUNK_HOST:
        return False, "Not configured", kwargs
    try:
        splunk_venture = Venture.objects.get(symbol='splunk_unknown_usage')
    except Venture.DoesNotExist:
        return False, 'Splunk venture does not exist!', kwargs
    usage_type, created = UsageType.objects.get_or_create(
        name="Splunk Volume 1 MB",
    )
    date = kwargs['today']
    splunk = Splunk()
    splunk.start()
    percent = splunk.progress
    while percent < 100:
        print(percent)
        time.sleep(30)
        percent = splunk.progress
    hosts = {}
    total_mb = 0
    for item in splunk.results:
        host = item['host']
        mb = float(item['MBytes'])
        total_mb += mb
        if host in hosts:
            hosts[host] += mb
        else:
            hosts[host] = mb
    for host, usage in hosts.iteritems():
        set_usages(date, usage, usage_type, host, splunk_venture)
    return True, 'done.', kwargs

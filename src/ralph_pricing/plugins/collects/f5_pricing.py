#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ralph pricing plugin to download and save BIGIP F5 cpu usage. Goal is to get
usages per device per venture for purpose of billing.
"""

import datetime
import logging

from django.conf import settings
from pycontrol import pycontrol

from ralph.util import plugin
from ralph_pricing.models import (
    UsageType,
    Venture,
    DailyUsage,
    Device,
)


logger = logging.getLogger(__name__)


WSDLS = [
    'LocalLB.VirtualServer',
    'LocalLB.PoolMember',
    'LocalLB.Pool',
    'Management.Partition',
]


def get_f5_usages(host):
    """
    Talk with given F5 and retrieves statistics data.
    """
    user = settings.F5_USER
    pwd = settings.F5_PASSWORD
    load_balancer = pycontrol.BIGIP(
        hostname=host,
        username=user,
        password=pwd,
        fromurl=True,
        wsdls=WSDLS,
    )
    lb_vs = load_balancer.LocalLB.VirtualServer
    lb_mp = load_balancer.Management.Partition
    statistics = []
    time = None
    for partition in lb_mp.get_partition_list():
        lb_mp.set_active_partition(partition.partition_name)
        vservs = lb_vs.get_list()
        if not vservs:
            continue
        stats = lb_vs.get_statistics(vservs)
        stats_time = stats[1]
        time = datetime.datetime(
            year=stats_time.year,
            month=stats_time.month,
            day=stats_time.day,
            hour=stats_time.hour,
            minute=stats_time.minute,
            second=stats_time.second,
        )
        stats_details = stats[0]
        zippd = zip(vservs, stats_details)
        statistics.extend(zippd)
    return statistics, time


def _set_usage(symbol, venture, device, value, total, time):
    usage_type, created = UsageType.objects.get_or_create(
        symbol=symbol,
        defaults=dict(
            name=symbol,
            average=True,
        )
    )
    usage, created = DailyUsage.objects.get_or_create(
        date=time,
        type=usage_type,
        pricing_venture=venture,
        pricing_device=device,
    )
    usage.value = value
    usage.total = total
    usage.save()


def _get_last_usage(symbol, venture, device):
    try:
        usage_type = UsageType.objects.get(symbol=symbol)
    except UsageType.DoesNotExist:
        return 0
    last_usage = DailyUsage.objects.filter(
        type=usage_type,
        pricing_venture=venture,
        pricing_device=device,
    ).order_by("-date")
    if last_usage:
        return last_usage[0].total
    return 0


def save_usages(usages):
    saved_records = 0
    for venture_symbol, usage in usages['usages'].iteritems():
        try:
            venture = Venture.objects.get(symbol=venture_symbol)
        except Venture.DoesNotExist:
            continue
        old_cpu = _get_last_usage(
            'f5',
            venture,
            usages['device'],
        )
        new_cpu = usage - old_cpu
        _set_usage(
            'f5',
            venture,
            usages['device'],
            new_cpu,
            usage,
            usages['time'],
        )
        saved_records += 1
    return saved_records


def parse_usages(usages, time, device):
    ret = {
        'device': device,
        'time': time
    }
    usage = {}
    for u in usages:
        vserv_name = u[0]
        try:
            # currently we name our vIPs as venture-hostname-protocol
            venture_symbol = vserv_name.split("/")[2].split("-")[0]
        except IndexError:
            logger.warning("wrong Virtual Server name: {}".format(vserv_name))
            continue
        cpu = filter(
            lambda s: s.type == "STATISTIC_VIRTUAL_SERVER_TOTAL_CPU_CYCLES",
            u[1][1],
        )[0]
        # unsigned_low = cpu.value.low & 0xffffffff  # to convert int to unsigned
        total_usage = cpu.value.high  # bit high and low order
        usage[venture_symbol] = usage.get(venture_symbol, 0) + total_usage
    ret['usages'] = usage
    return ret


@plugin.register(chain='pricing', requires=['ventures'])
def f5_pricing(**kwargs):
    saved_records = 0
    for host in settings.F5_HOSTNAMES:
        print (host)
        try:
            device = Device.objects.get(name=host)
            usages, time = get_f5_usages(host)
            if not usages or not time:
                continue
            usages_parsed = parse_usages(usages, time, device)
            saved_records += save_usages(usages_parsed)
        except Exception, e:
            logger.exception(e)
    return True, 'F5 Usages: {} records saved'.format(saved_records), kwargs

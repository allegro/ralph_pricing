import datetime
import logging

from pycontrol import pycontrol
from django.conf import settings

from ralph.util import plugin
from ralph_pricing.models import (
    UsageType,
    Venture,
    DailyUsage,
    Device,
)


logger = logging.getLogger(__name__)


wsdls = [
    'LocalLB.VirtualServer',
    'LocalLB.PoolMember',
    'LocalLB.Pool',
    'Management.Partition',
]


def get_f5_usages(host):
    """
    This function talks with given F5 and retrieves statistics data.
    """
    user = settings.F5_USER
    pwd = settings.F5_PASSWORD
    lb = pycontrol.BIGIP(
        hostname=host,
        username=user,
        password=pwd,
        fromurl=True,
        wsdls=wsdls,
    )
    lb_vs = lb.LocalLB.VirtualServer
    lb_mp = lb.Management.Partition
    statistics = []
    for partition in lb_mp.get_partition_list():
        lb_mp.set_active_partition(partition.partition_name)
        vservs = lb_vs.get_list()
        if not vservs:
            continue
        stats = lb_vs.get_statistics(vservs)
        time = datetime.datetime(
            year=stats[1].year,
            month=stats[1].month,
            day=stats[1].day,
            hour=stats[1].hour,
            minute=stats[1].minute,
            second=stats[1].second,
        )
        stats = stats[0]
        zippd = zip(vservs, stats)
        statistics += zippd
    return statistics, time


def _set_usage(symbol, venture, device, value, total, time):
    usage_type, created = UsageType.objects.get_or_create(
        name=symbol,  # should be edited in admin later
        symbol=symbol,
    )
    usage, created = DailyUsage.objects.get_or_create(
        date=time,
        type=usage_type,
        pricing_venture=venture,
    )
    usage.value = value
    usage.total = total
    usage.pricing_device = device
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
    for venture_symbol, usage in usages['usages'].iteritems():
        try:
            venture = Venture.objects.get(symbol=venture_symbol)
        except Venture.DoesNotExist:
            continue
        old_cpu = _get_last_usage(
            'f5_cpu_usage',
            venture,
            usages['device'],
        )
        new_cpu = usage - old_cpu
        _set_usage(
            'f5_cpu_usage',
            venture,
            usages['device'],
            new_cpu,
            usage,
            usages['time'],
        )


def get_f5_hostnames():
    return settings.F5_HOSTNAMES


def parse_usages(usages, time, device):
    ret = {
        'device': device,
        'time': time
    }
    usage = {}
    for u in usages:
        vserv_name = u[0]
        try:
            venture_symbol = vserv_name.split("/")[2].split("-")[0]
        except IndexError:
            continue
        cpu = filter(
            lambda s: s.type == "STATISTIC_VIRTUAL_SERVER_TOTAL_CPU_CYCLES",
            u[1][1],
        )[0]
        total_usage = cpu.value.low + (cpu.value.high << 32)  # bit high and low order
        usage[venture_symbol] = usage.get(venture_symbol, 0) + abs(total_usage)
    ret['usages'] = usage
    return ret


@plugin.register(chain='pricing', requires=['ventures'])
def f5(**kwargs):
    for host in get_f5_hostnames():
        try:
            device = Device.objects.get(name=host)
            usages, time = get_f5_usages(host)
            usages_parsed = parse_usages(usages, time, device)
            save_usages(usages_parsed)
        except Exception, e:
            logger.exception("Error while getting F5 usages: {}".format(host))
    return True, 'F5 Usages saved', kwargs

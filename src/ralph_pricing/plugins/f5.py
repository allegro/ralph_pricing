import datetime

from pycontrol import pycontrol
from django.conf import settings

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage


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
        profiles = lb_vs.get_profile(vservs)
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
        zippd = zip(vservs, profiles, stats)
        statistics += zippd
    return statistics, time


def _set_usage(symbol, venture, value, total, time):
    usage_type, created = UsageType.objects.get_or_create(
        name=symbol,  # temporary value, should be set up afterwards to something human friendly
        symbol=symbol,
    )
    usage, created = DailyUsage.objects.get_or_create(
        date=time,
        type=usage_type,
        pricing_venture=venture,
    )
    usage.value = value
    usage.total = total
    usage.save()


def _get_last_usage(symbol, venture):
    try:
        usage_type = UsageType.objects.get(symbol=symbol)
    except UsageType.DoesNotExist:
        return 0
    last_usage = DailyUsage.objects.filter(
        type=usage_type,
        pricing_venture=venture,
    ).order_by("-date")
    if last_usage:
        return last_usage[0].total
    return 0


def save_usages(usages):
    for usage in usages.itervalues():
        old_normal = _get_last_usage(
            'f5_packages_normal',
            usage['venture'],
        )
        new_normal = usage['throughput_normal'] - old_normal
        _set_usage(
            'f5_packages_normal',
            usage['venture'],
            new_normal,
            usage['throughput_normal'],
            usage['time'],
        )

        old_performance = _get_last_usage(
            'f5_packages_performance',
            usage['venture'],
        )
        new_performance = usage['throughput_performance'] - old_performance
        _set_usage(
            'f5_packages_performance',
            usage['venture'],
            new_performance,
            usage['throughput_performance'],
            usage['time'],
        )


def parse_usages(usages, time):
    vent_usage = {}
    for vserv in usages:
        vserv_name = vserv[0]
        try:
            venture = Venture.objects.get(symbol=vserv_name.split("-")[0])
            if venture.symbol not in vent_usage:
                vent_usage[venture.symbol] = {
                    'throughput_performance': 0,
                    'throughput_normal': 0,
                    'ssl_trans': 0,
                    'venture': venture,
                    'time': time,
                }
        except Venture.DoesNotExist:
            continue
        throughput = 0
        for stat in vserv[2][1]:
            if stat.type in (
                'STATISTIC_CLIENT_SIDE_PACKETS_IN',
                'STATISTIC_CLIENT_SIDE_PACKETS_OUT',
            ):
                throughput += stat.value.low + stat.value.high
                # adding because its bitwise high-order and low-order number
        is_performance = False
        for profile in vserv[1]:
            if profile.profile_name == 'fastL4':
                is_performance = True
        if is_performance:
            vent_usage[venture.symbol]['throughput_performance'] += throughput
        else:
            vent_usage[venture.symbol]['throughput_normal'] += throughput
    return vent_usage


@plugin.register(chain='pricing', requires=['ping', 'http'])
def f5(**kwargs):
    host = 'f5-1a.te2'
    usages, time = get_f5_usages(host)
    usages_parsed = parse_usages(usages, time)
    save_usages(usages_parsed)
    return True, 'F5 Usages saved', kwargs

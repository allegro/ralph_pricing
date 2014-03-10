# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import collections
import logging


from django.conf import settings

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage
from ralph_pricing.openstack import OpenStack


logger = logging.getLogger(__name__)


def set_usages(venture_symbol, data, date):
    try:
        venture = Venture.objects.get(symbol=venture_symbol)
    except Venture.DoesNotExist:
        logger.warning('Venture: %s does not exist' % venture_symbol)
        return

    def set_usage(name, key, venture, multiplier):
        if key not in data:
            return
        usage_type, created = UsageType.objects.get_or_create(name=name)
        usage, created = DailyUsage.objects.get_or_create(
            date=date,
            type=usage_type,
            pricing_venture=venture,
        )
        usage.value = data[key] / multiplier
        usage.save()
    if venture:
        set_usage(
            'OpenStack 10000 Memory GiB Hours',
            'total_memory_mb_usage',
            venture,
            1024,
        )
        set_usage(
            'OpenStack 10000 CPU Hours',
            'total_vcpus_usage',
            venture,
            1,
        )
        set_usage(
            'OpenStack 10000 Disk GiB Hours',
            'total_local_gb_usage',
            venture,
            1,
        )
        set_usage(
            'OpenStack 10000 Volume GiB Hours',
            'total_volume_gb_usage',
            venture,
            1,
        )
        set_usage(
            'OpenStack 10000 Images GiB Hours',
            'total_images_gb_usage',
            venture,
            1,
        )


@plugin.register(chain='pricing', requires=['ventures'])
def openstack(**kwargs):
    """Updates OpenStack usage per Venture"""
    if settings.OPENSTACK_URL is None:
        return False, 'Not configured.', kwargs
    tenants = collections.defaultdict(lambda: collections.defaultdict(dict))
    date = kwargs['today']
    end = date
    start = end - datetime.timedelta(days=1)
    ventures = {}
    for region in getattr(settings, 'OPENSTACK_REGIONS', ['']):
        stack = OpenStack(
            settings.OPENSTACK_URL,
            settings.OPENSTACK_USER,
            settings.OPENSTACK_PASS,
            region=region,
        )
        ventures.update(stack.get_ventures())
        for data in stack.simple_tenant_usage(start, end):
            tenants[data['tenant_id']][region].update(data)
    for url, query in getattr(settings, 'OPENSTACK_EXTRA_QUERIES', []):
        for data in stack.query(
            query,
            url=url,
            start=start.strftime('%Y-%m-%dT%H:%M:%S'),
            end=end.strftime('%Y-%m-%dT%H:%M:%S'),
        ):
            tenants[data['tenant_id']][url].update(data)
    for tenant_id, regions in tenants.iteritems():
        for region, data in regions.iteritems():
            venture_symbol = ventures.get(data['tenant_id'])
            if venture_symbol:
                set_usages(venture_symbol, data, date)
    return True, 'Openstack usages were saved', kwargs

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import collections
import re


from django.conf import settings
from lck.django.common import nested_commit_on_success

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage
from ralph_pricing.openstack import Openstack


VENTURE = re.compile('venture:(?P<venture>.*);')


@nested_commit_on_success
def set_usages(venture, data):
    venture = Venture.objects.get(symbol=venture)
    def set_usage(name, key, venture, multiplier):
        if key not in data:
            return
        usage_type, created = UsageType.objects.get_or_create(name=name)
        try:
            time = datetime.datetime.strptime(data['stop'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            time = datetime.datetime.strptime(data['stop'], '%Y-%m-%dT%H:%M:%S')
        usage, created = DailyUsage.objects.get_or_create(
            date=time.date(),
            type=usage_type,
            pricing_venture=venture,
        )
        usage.value = data[key] / multiplier
        usage.save()
    if venture:
        set_usage('OpenStack 10000 Memory GiB Hours','total_memory_mb_usage',
                   venture, 1024)
        set_usage('OpenStack 10000 CPU Hours','total_vcpus_usage',
                   venture, 1)
        set_usage('OpenStack 10000 Disk GiB Hours','total_local_gb_usage',
                   venture, 1)
        set_usage('OpenStack 10000 Volume GiB Hours','total_volume_gb_usage',
                   venture, 1)
        set_usage('OpenStack 10000 Images GiB Hours','total_images_gb_usage',
                   venture, 1)


@plugin.register(chain='pricing', requires=['sync_ventures'])
def openstack(**kwargs):
    """Updates Openstack usage per Venture"""
    if settings.OPENSTACK_URL is None:
        return False, 'not configured.', kwargs
    tenants = collections.defaultdict(lambda: collections.defaultdict(dict))
    end = datetime.datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start = end - datetime.timedelta(days=1)
    for region in getattr(settings, 'OPENSTACK_REGIONS', ['']):
        stack = Openstack(
            settings.OPENSTACK_URL,
            settings.OPENSTACK_USER,
            settings.OPENSTACK_PASS,
            region=region,
        )
        for data in stack.simple_tenant_usage(start, end):
            tenants[data['tenant_id']][region].update(data)
    for url, query in getattr(settings, 'OPENSTACK_EXTRA_QUERIES', []):
        ventures = {}
        if query == 'tenants':
            result = stack.query(query, url=url, limit=1000)
            for data in result['tenants']:
                if data['enabled'] == True:
                    venture = None
                    description = data.get('description')
                    if description:
                        result = re.match(VENTURE, description)
                        if result:
                            venture = result.group('venture')
                    ventures[data['id']] = venture
        else:
            for data in stack.query(query, url=url,
                    start=start.strftime('%Y-%m-%dT%H:%M:%S'),
                    end=end.strftime('%Y-%m-%dT%H:%M:%S'),
                ):
                tenants[data['tenant_id']][url].update(data)
    for tenant_id, regions in tenants.iteritems():
        for region, data in regions.iteritems():
            venture = ventures.get(data['tenant_id'])
            if venture:
                set_usages(venture, data)
    return True, 'Openstack usages was saved', kwargs







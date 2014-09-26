# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta
import logging

from django.conf import settings
from novaclient.v1_1 import client as nova_client

from ralph.util import plugin
from ralph_scrooge.models import DailyUsage, TenantInfo, UsageType, Warehouse

logger = logging.getLogger(__name__)

USAGE_SYMBOL_TMPL = 'openstack_simple.{}'
USAGES = [
    ('total_memory_mb_usage', 'OpenStack Memory MB'),
    ('total_vcpus_usage', 'OpenStack VCPU'),
    ('total_local_gb_usage', 'OpenStack Disk GiB'),
    ('total_volume_gb_usage', 'OpenStack Volume GiB'),
    ('total_images_gb_usage', 'OpenStack Images GiB'),
]


def save_usage(usage, date, usage_types, warehouse):
    try:
        tenant = TenantInfo.objects.get(tenant_id=usage.tenant_id)
    except TenantInfo.DoesNotExist:
        logger.error('Tenant {} not found'.format(usage.tenant_id))
        return False
    usage_dict = usage.to_dict()
    daily_tenant = tenant.get_daily_pricing_object(date)
    for usage_symbol, usage_type in usage_types.iteritems():
        value = usage_dict.get(usage_symbol)
        if value:
            DailyUsage.objects.create(
                date=date,
                service_environment=daily_tenant.service_environment,
                daily_pricing_object=daily_tenant,
                value=value,
                type=usage_type,
                warehouse=warehouse,
            )
    return True


def clear_openstack_simple_usages(date):
    logger.debug('Clearing OpenStack simple usages for {}'.format(date))
    DailyUsage.objects.filter(
        type__symbol__startswith=USAGE_SYMBOL_TMPL.format(''),
        date=date,
    ).delete()


def get_usage_types():
    usages = {}
    for usage_symbol, usage_name in USAGES:
        usage_type, created = UsageType.objects.get_or_create(
            symbol=USAGE_SYMBOL_TMPL.format(usage_symbol),
            defaults=dict(
                name=usage_name,
                by_warehouse=True,
                by_cost=False,
                average=False,
                usage_type='SU'
            ),
        )
        usages[usage_symbol] = usage_type
    return usages


def get_usages(site, region, start, end):
    nova = nova_client.Client(
        site['USERNAME'],
        site['PASSWORD'],
        site['TENANT_NAME'],
        site['AUTH_URL'],
        region_name=region,
        service_type="compute",
    )
    return nova.usage.list(
        start=start,
        end=end
    )


@plugin.register(chain='scrooge', requires=['service', 'tenant'])
def openstack_simple_usage(today, **kwargs):
    """
    Pricing plugin for openstack simple usages
    """
    clear_openstack_simple_usages(today)
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(days=1)
    success = total = 0
    usage_types = get_usage_types()
    for site in settings.OPENSTACK_SIMPLE_USAGES:
        for region in site['REGIONS']:
            region_success = 0
            logger.info("Processing OpenStack site {} {}".format(
                site['AUTH_URL'],
                region,
            ))

            try:
                warehouse = Warehouse.objects.get(name=region)
            except Warehouse.DoesNotExist:
                logger.error('Invalid warehouse for site {}: {}'.format(
                    site['AUTH_URL'],
                    region,
                ))
                continue
            usages = get_usages(site, region, start, end)
            for usage in usages:
                if save_usage(usage, today, usage_types, warehouse):
                    region_success += 1
            logger.info('{} usages saved, {} total'.format(
                region_success,
                len(usages)
            ))
            total += len(usages)
            success += region_success
    return True, 'OpenStack simple usages: {} success, {} total'.format(
        success,
        total
    )

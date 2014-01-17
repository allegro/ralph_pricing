# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging

from django.conf import settings
from ceilometerclient.client import get_client
from keystoneclient.client import Client

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage


logger = logging.getLogger('ralph')


def get_tenants(client):
    tenants = [
        ('4d9d8413547c4626a0a1bb9feca988cb', "whatever;agito"),
    ]
    return tenants


def get_ceilometer_usages(client, tenants, date=None):
    date = date or datetime.date.today()
    today = datetime.datetime.combine(date, datetime.datetime.min.time())
    yesterday = today - datetime.timedelta(days=1)
    meters = [
        'cpu',
        'network.outgoing.bytes',
        'network.incoming.bytes',
    ]
    statistics = {}
    for tenant in tenants:
        tenant_venture = tenant[1].split(";")[1]
        statistics[tenant_venture] = {}
        for meter in meters:
            query = [
                {
                    'field': 'project_id',
                    'op': 'eq',
                    'value': tenant[0],
                },
                {
                    "field": "timestamp",
                    "op": "ge",
                    "value": yesterday.isoformat(),
                },
                {
                    "field": "timestamp",
                    "op": "lt",
                    "value": today.isoformat(),
                },
            ]
            logger.debug(
                "[CEILOMETER] stats {}-{} tenant: {} metric: {}".format(
                    yesterday.isoformat(),
                    today.isoformat(),
                    tenant_venture,
                    meter,
                )
            )
            stats = client.statistics.list(meter_name=meter, q=query)[0]
            if not meter in statistics[tenant_venture]:
                statistics[tenant_venture][meter] = 0
            statistics[tenant_venture][meter] += stats.sum
            logger.debug("[CEILOMETER] {}:{}:{}{}".format(
                tenant_venture,
                meter,
                stats.sum,
                stats.unit,
            ))
    return statistics


def save_ceilometer_usages(usages, date):
    def set_usage(usage_symbol, venture, value, date):
        usage_type, created = UsageType.objects.get_or_create(
            symbol=usage_symbol,
        )
        if not usage_type.name:
            usage_type.name = "openstack." + usage_symbol
            usage_type.save()
        usage, created = DailyUsage.objects.get_or_create(
            date=date,
            type=usage_type,
            pricing_venture=venture,
        )
        usage.value = value
        usage.save()

    for venture_symbol, usages in usages.iteritems():
        try:
            venture = Venture.objects.get(symbol=venture_symbol)
        except Venture.DoesNotExist:
            logger.error(
                "[CEILOMETER] Venture with symbol {} does not exist".format(
                    venture_symbol,
                )
            )
            continue
        for usage_symbol, value in usages.iteritems():
            set_usage(usage_symbol, venture, value, date)


@plugin.register(chain='pricing', requires=['ventures'])
def ceilometer(**kwargs):
    logger.info("[CEILOMETER] start {}".format(
        datetime.datetime.now().isoformat(),
    ))
    for site in settings.OPENSTACK_SITES:
        logger.info("[CEILOMETER] site {}".format(
            site['OS_METERING_URL'],
        ))
        keystone_client = Client(
            username=site['OS_USERNAME'],
            password=site['OS_PASSWORD'],
            tenant_name=site['OS_TENANT_NAME'],
            auth_url=site['OS_AUTH_URL'],
        )
        tenants = get_tenants(keystone_client)
        ceilo_client = get_client(
            "2",
            ceilometer_url=site['OS_METERING_URL'],
            os_username=site['OS_USERNAME'],
            os_password=site['OS_PASSWORD'],
            os_auth_url=site['OS_AUTH_URL'],
            os_tenant_name=site['OS_TENANT_NAME'],
        )
        stats = get_ceilometer_usages(
            ceilo_client,
            tenants,
            date=kwargs['today'],
        )
        save_ceilometer_usages(stats, date=kwargs['today'])

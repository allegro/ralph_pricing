# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import logging

import requests

from ceilometerclient.client import get_client
from django.conf import settings

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage


logger = logging.getLogger('ralph')


def get_token(site):
    data = {
        "auth": {
            "passwordCredentials": {
                "username": site['OS_USERNAME'],
                "password": site['OS_PASSWORD'],
            }
        }
    }
    token = requests.post(
        site['OS_AUTH_URL'] + "/tokens",
        data=json.dumps(data),
        headers={
            'content-type': 'application/json',
        },
    )
    return json.loads(str(token.content))['access']['token']['id']


def get_tenants(site):
    """
    For some reason keystoneclient forcibly use admin endpoint.
    """
    headers_tenant = {
        'X-Auth-Token': get_token(site),
        'content-type': 'application/json',
    }
    tenants_url = site['OS_AUTH_URL'] + "/tenants"
    tenants = requests.get(tenants_url, headers=headers_tenant)
    return json.loads(str(tenants.content)).get('tenants', [])


def get_ceilometer_usages(client, tenants, date=None):
    """
    Function which talks with openstack
    """
    date = date or datetime.date.today()
    today = datetime.datetime.combine(date, datetime.datetime.min.time())
    yesterday = today - datetime.timedelta(days=1)
    meters = [
        'cpu',
        'network.outgoing.bytes',
        'network.incoming.bytes',
        'disk.write.requests',
        'disk.read.requests',
    ]
    statistics = {}
    for tenant in tenants:
        try:
            tenant_venture = tenant['description'].split(";")[1]
        except (ValueError, IndexError):
            logger.error(
                "Tenant malformed: {}".format(str(tenant))
            )
            continue
        statistics[tenant_venture] = {}
        for meter in meters:
            query = [
                {
                    'field': 'project_id',
                    'op': 'eq',
                    'value': tenant['id'],
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
                "stats {}-{} tenant: {} metric: {}".format(
                    yesterday.isoformat(),
                    today.isoformat(),
                    tenant_venture,
                    meter,
                )
            )
            try:
                stats = client.statistics.list(meter_name=meter, q=query)[0]
            except IndexError:
                logger.warning(
                    "No statistics for tenant {}".format(
                        tenant['id']
                    )
                )
                continue
            if not meter in statistics[tenant_venture]:
                statistics[tenant_venture][meter] = 0
            statistics[tenant_venture][meter] += stats.sum
            logger.debug("{}:{}:{}{}".format(
                tenant_venture,
                meter,
                stats.sum,
                stats.unit,
            ))
    return statistics


def save_ceilometer_usages(usages, date):
    """
    takes usages as input and saves them to database
    """
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
        logger.info("Usages saved {}:{}".format(venture, value))

    for venture_symbol, usages in usages.iteritems():
        try:
            venture = Venture.objects.get(symbol=venture_symbol)
        except Venture.DoesNotExist:
            logger.error(
                "Venture with symbol {} does not exist".format(
                    venture_symbol,
                )
            )
            continue
        for usage_symbol, value in usages.iteritems():
            set_usage(usage_symbol, venture, value, date)


@plugin.register(chain='pricing', requires=['ventures'])
def ceilometer(**kwargs):
    """
    Pricing plugin for openstack havana- ceilometer.
    """
    logger.info("start {}".format(
        datetime.datetime.now().isoformat(),
    ))
    for site in settings.OPENSTACK_SITES:
        logger.info("site {}".format(
            site['OS_METERING_URL'],
        ))
        tenants = get_tenants(site)
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
    return True, 'ceilometer usages saved', kwargs

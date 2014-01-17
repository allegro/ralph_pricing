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


OS_METERING_URL = "http://10.196.239.10:8777"
OS_TENANT_NAME = 'admin'
OS_USERNAME = 'admin'
OS_PASSWORD = 'Aid9aira'
OS_AUTH_URL = "http://10.196.239.10:5000/v2.0"

logger = logging.getLogger('ralph')


def get_tenants():
    """
    keystone = Client(
        username=OS_USERNAME,
        password=OS_PASSWORD,
        tenant_name=OS_TENANT_NAME,
        auth_url=OS_AUTH_URL,
    )"""
    tenants = [
        '4d9d8413547c4626a0a1bb9feca988cb',
    ]
    return tenants


def get_ceilometer_usages(date=None):
    date = date or datetime.date.today()
    today = datetime.datetime.combine(date, datetime.datetime.min.time())
    yesterday = today - datetime.timedelta(days=1)
    client = get_client(
        "2",
        ceilometer_url=OS_METERING_URL,
        os_username=OS_USERNAME,
        os_password=OS_PASSWORD,
        os_auth_url=OS_AUTH_URL,
        os_tenant_name=OS_TENANT_NAME,
    )
    tenants = get_tenants()
    meters = [
        'cpu',
        'network.outgoing.bytes',
        'network.incoming.bytes',
    ]
    statistics = {}
    for meter in meters:
        statistics[meter] = {}
        for tenant in tenants:
            query = [
                {
                    'field': 'project_id',
                    'op': 'eq',
                    'value': tenant,
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
                    tenant,
                    meter,
                )
            )
            stats = client.statistics.list(meter_name=meter, q=query)[0]
            statistics[meter][tenant] = stats.sum
            logger.debug("[CEILOMETER] {}:{}:{}{}".format(
                tenant,
                meter,
                stats.sum,
                stats.unit,
            ))
    return statistics


@plugin.register(chain='pricing', requires=['ventures'])
def ceilometer(**kwargs):
    logger.info("[CEILOMETER] start {}".format(
        datetime.datetime.now().isoformat(),
    ))
    stats = get_ceilometer_usages()

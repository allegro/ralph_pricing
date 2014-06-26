# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging

from django.conf import settings
from ceilometerclient.client import get_client
from keystoneclient.v2_0 import client
from novaclient.v1_1 import client as nova_client

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage


logger = logging.getLogger(__name__)


def get_ceilometer_usages(
    client,
    tenants,
    flavors,
    statistics,
    date=None,
):
    """
    Function which talks with openstack
    """
    date = date or datetime.date.today()
    today = datetime.datetime.combine(date, datetime.datetime.min.time())
    yesterday = today - datetime.timedelta(days=1)
    for tenant in tenants:
        logger.debug('Getting stats for tenant {}: {}/{}'.format(
            tenant.name, tenants.index(tenant), len(tenants),
        ))
        try:
            tenant_venture = tenant.description.split(";")[1]
        except (ValueError, IndexError, AttributeError):
            logger.warning(
                "Tenant malformed: {}".format(tenant.id)
            )
            continue
        except AttributeError:
            logger.warning(
                "Tenant {0} has no description".format(tenant.id)
            )
            continue
        statistics[tenant_venture] = statistics.get(tenant_venture, {})
        query = [
            {
                'field': 'project_id',
                'op': 'eq',
                'value': tenant.id,
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
        aggregates = [{'func': 'cardinality', 'param': 'resource_id'}]
        logger.debug("Getting instance usage for tenant {}".format(
            tenant.name
        ))
        for flav in flavors:
            meter = "instance:{}".format(flav)
            stats = client.statistics.list(
                meter,
                q=query,
                period=3600,
                aggregates=aggregates,
            )
            icount = 0
            for sample in stats:
                icount += sample.aggregate.get('cardinality/resource_id', 0)
            meter_name = 'instance.{}'.format(flav)
            statistics[tenant_venture]['openstack.' + meter_name] = statistics[
                tenant_venture
            ].get('openstack.' + meter_name, 0) + icount
            logger.debug("Got statistics {}:{} for tenant {}".format(
                meter, icount, tenant.name,
            ))
    return statistics


def save_ceilometer_usages(usages, date):
    """
    takes usages as input and saves them to database
    """
    def set_usage(usage_symbol, venture, value, date):
        usage_type, created = UsageType.objects.get_or_create(
            symbol=usage_symbol,
            defaults=dict(
                name=usage_symbol,
            ),
        )
        usage, created = DailyUsage.objects.get_or_create(
            date=date,
            type=usage_type,
            pricing_venture=venture,
        )
        usage.value = value
        usage.save()
        logger.info("Usages saved {},{}:{}".format(
            venture,
            "openstack." + usage_symbol,
            value,
        ))

    for venture_symbol, usages in usages.iteritems():
        try:
            venture = Venture.objects.get(symbol=venture_symbol)
        except Venture.DoesNotExist:
            logger.warning(
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
    stats = {}
    for site in settings.OPENSTACK_SITES:
        logger.info("site {}".format(
            site['OS_METERING_URL'],
        ))
        ks = client.Client(
            username=site['OS_USERNAME'],
            password=site['OS_PASSWORD'],
            tenant_name=site['OS_TENANT_NAME'],
            auth_url=site['OS_AUTH_URL'],
        )
        tenants = ks.tenants.list()
        ceilo_client = get_client(
            "2",
            ceilometer_url=site['OS_METERING_URL'],
            os_username=site['OS_USERNAME'],
            os_password=site['OS_PASSWORD'],
            os_auth_url=site['OS_AUTH_URL'],
            os_tenant_name=site['OS_TENANT_NAME'],
        )
        nova = nova_client.Client(
            site['OS_USERNAME'],
            site['OS_PASSWORD'],
            site['OS_TENANT_NAME'],
            site['OS_AUTH_URL'],
            service_type="compute",
        )
        flavors = [f.name for f in nova.flavors.list()]
        stats = get_ceilometer_usages(
            ceilo_client,
            tenants,
            date=kwargs['today'],
            flavors=flavors,
            statistics=stats,
        )
    save_ceilometer_usages(stats, date=kwargs['today'])
    return True, 'ceilometer usages saved', kwargs

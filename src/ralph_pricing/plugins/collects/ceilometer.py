# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import time

from django.conf import settings
from keystoneclient.v2_0 import client
from sqlalchemy import create_engine

from ralph.util import plugin
from ralph_pricing.models import UsageType, Venture, DailyUsage


logger = logging.getLogger(__name__)


def get_ceilometer_usages(
    tenants,
    statistics,
    connection_string,
    date=None,
):
    """
    Function which talks with openstack
    """
    date = date or datetime.date.today()
    today = datetime.datetime.combine(date, datetime.datetime.min.time())
    yesterday = today - datetime.timedelta(days=1)
    engine = create_engine(connection_string)
    connection = engine.connect()
    for tenant in tenants:
        logger.info('Getting stats for tenant {}: {}/{}'.format(
            tenant.name, tenants.index(tenant), len(tenants),
        ))
        try:
            tenant_venture = tenant.description.split(";")[1]
        except (ValueError, IndexError, AttributeError):
            logger.warning(
                'Tenant malformed: {}'.format(tenant.id)
            )
            continue
        except AttributeError:
            logger.warning(
                'Tenant {0} has no description'.format(tenant.id)
            )
            continue
        statistics[tenant_venture] = statistics.get(tenant_venture, {})
        query = (
            'select count(*) as count, meter.name as flavor'
            ' from sample left join meter on'
            ' sample.meter_id = meter.id where meter.name like "instance:%%"'
            ' and sample.project_id = "{tenant_id}"'
            ' and timestamp < {to_ts} and timestamp > {from_ts}'
            ' and cast(timestamp as unsigned) = timestamp'
            ' group by sample.meter_id'
        ).format(
            tenant_id=tenant.id,
            from_ts=time.mktime(yesterday.timetuple()),
            to_ts=time.mktime(today.timetuple()),
        )
        res = connection.execute(query)
        for flavor_stats in res:
            metric_name = 'openstack.' + flavor_stats[
                'flavor'
            ].replace(":", ".")
            statistics[tenant_venture][metric_name] = (
                (flavor_stats['count'] / 6) + statistics[tenant_venture].get(
                    metric_name,
                    0,
                )
            )
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
                show_in_ventures_report=False,
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
        if 'CEILOMETER_CONNECTION' not in site:
            logger.warning('CEILOMETER_CONNECTION not specified')
            continue
        logger.info("site {}".format(
            site['OS_METERING_URL'],
        ))
        ks = client.Client(
            username=site['USERNAME'],
            password=site['PASSWORD'],
            tenant_name=site['TENANT_NAME'],
            auth_url=site['AUTH_URL'],
        )
        tenants = ks.tenants.list()
        stats = get_ceilometer_usages(
            tenants,
            date=kwargs['today'],
            statistics=stats,
            connection_string=site['CEILOMETER_CONNECTION']
        )
    save_ceilometer_usages(stats, date=kwargs['today'])
    return True, 'ceilometer usages saved', kwargs

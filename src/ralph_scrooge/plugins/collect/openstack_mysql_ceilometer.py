# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import time

from django.conf import settings
from ralph_scrooge.utils.common import memoize
from sqlalchemy import create_engine

from ralph.util import plugin
from ralph_scrooge.models import (
    DailyTenantInfo,
    DailyUsage,
    TenantInfo,
    UsageType,
    Warehouse
)


logger = logging.getLogger(__name__)

METRIC_TMPL = 'openstack.{}'
CEILOMETER_QUERY = """
select sample.project_id, count(sample.id) as count, meter.name as flavor
from sample
    left join meter on sample.meter_id = meter.id
where
    meter.name like "instance:%%"
    and timestamp < {to_ts} and timestamp > {from_ts}
    and cast(timestamp as unsigned) = timestamp
group by sample.meter_id, sample.project_id
"""


class TenantNotFoundError(Exception):
    """
    Raised when tenant info does not exist
    """
    pass


class DailyTenantNotFoundError(Exception):
    """
    Raised when daily tenant info does not exist
    """
    pass


@memoize
def get_usage_type(flavor_name):
    usage_name = METRIC_TMPL.format(flavor_name)
    usage_symbol = usage_name.lower().replace(':', '.').replace(' ', '_')
    return UsageType.objects.get_or_create(
        symbol=usage_symbol,
        defaults=dict(
            name=usage_name,
            show_in_services_report=False,
            type='SU',
        ),
    )[0]


@memoize
def get_daily_tenant(tenant_id, date):
    try:
        tenant = TenantInfo.objects.get(tenant_id=tenant_id)
        return tenant.daily_tenants.get(date=date)
    except TenantInfo.DoesNotExist as e:
        raise TenantNotFoundError(e)
    except DailyTenantInfo.DoesNotExist as e:
        raise DailyTenantNotFoundError(e)


def get_ceilometer_usages(date, connection_string):
    """
    Function which talks with openstack
    """
    today = datetime.datetime.combine(date, datetime.datetime.min.time())
    yesterday = today - datetime.timedelta(days=1)

    engine = create_engine(connection_string)
    connection = engine.connect()
    query = CEILOMETER_QUERY.format(
        from_ts=time.mktime(yesterday.timetuple()),
        to_ts=time.mktime(today.timetuple())
    )
    return connection.execute(query)


def save_ceilometer_usages(usages, date, warehouse):
    new = total = 0
    for tenant_id, value, flavor_name in usages:
        total += 1
        usage_type = get_usage_type(flavor_name)
        try:
            daily_tenant = get_daily_tenant(tenant_id, date)
        except TenantNotFoundError:
            logger.error('Tenant {} not found'.format(tenant_id))
            continue
        except DailyTenantNotFoundError:
            logger.error('DailyTenant {} for date {} not found'.format(
                tenant_id,
                date,
            ))
            continue
        DailyUsage(
            date=date,
            service_environment=daily_tenant.service_environment,
            daily_pricing_object=daily_tenant,
            value=value / 6.0,  # ceilometer usages are saved each 10 minutes
            type=usage_type,
            warehouse=warehouse,
        ).save()
        new += 1
    return new, total


def clear_ceilometer_stats(date):
    logger.debug('Clearing ceilometer records for {}'.format(date))
    DailyUsage.objects.filter(
        type__symbol__startswith=METRIC_TMPL.format(''),
        date=date,
    ).delete()


@plugin.register(chain='scrooge', requires=['service', 'tenant'])
def openstack_mysql_ceilometer(today, **kwargs):
    """
    Pricing plugin for openstack ceilometer.
    """
    clear_ceilometer_stats(today)
    new = total = 0
    for site in settings.OPENSTACK_CEILOMETER:
        logger.info(
            "Processing OpenStack ceilometer {}".format(site['WAREHOUSE'])
        )
        try:
            warehouse = Warehouse.objects.get(name=site['WAREHOUSE'])
        except Warehouse.DoesNotExist:
            logger.error('Invalid warehouse: {}'.format(
                site['WAREHOUSE']
            ))
            continue
        usages = get_ceilometer_usages(today, site['CEILOMETER_CONNECTION'])
        site_new, site_total = save_ceilometer_usages(usages, today, warehouse)

        logger.info(
            '{} new, {} total ceilometer usages saved for {}'.format(
                site_new,
                site_total,
                site['WAREHOUSE'],
            )
        )

        new += site_new
        total += site_total

    return True, 'Ceilometer usages: {} new, {} total'.format(new, total)

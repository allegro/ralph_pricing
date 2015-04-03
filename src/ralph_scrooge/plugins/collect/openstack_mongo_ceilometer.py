# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
from itertools import chain

from django.conf import settings
from ralph_scrooge.utils.common import memoize
from pymongo import MongoClient

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
    client = MongoClient(connection_string)
    db = client.ceilometer
    cumulative_data = db.meter.aggregate([
        {
            "$match": {
                "timestamp": {"$gt": yesterday, "$lt": today},
                "counter_type": "cumulative"
            }
        },
        {
            "$group": {
                "_id": {
                    "project_id": "$project_id",
                    "counter_name": "$counter_name"
                },
                "counter_max": {"$max": "$counter_volume"},
                "counter_min": {"$min": "$counter_volume"}
            }
        },
        {
            "$project": {
                "_id": {
                    "project_id": 1,
                    "counter_name": 1
                },
                "value": {
                    "$subtract": ["$counter_max", "$counter_min"]
                }
            }
        },
    ])
    gauge_data = db.meter.aggregate([
        {
            "$match": {
                "timestamp": {"$gt": yesterday, "$lt": today},
                "counter_type": "gauge"
            }
        },
        {
            "$group": {
                "_id": {
                    "project_id": "$project_id",
                    "counter_name": "$counter_name"
                },
                "total": {"$sum": "$counter_volume"}
            }
        },
        {
            "$project": {
                "_id": {"project_id": 1, "counter_name": 1},
                "value": {"$divide": ["$total", 144]}
            }
        },
    ])
    delta_data = db.meter.aggregate([
        {
            "$match": {
                "timestamp": {"$gt": yesterday, "$lt": today},
                "counter_type": "delta"
            }
        },
        {
            "$group": {
                "_id": {
                    "project_id": "$project_id",
                    "counter_name": "$counter_name"
                },
                "value": {"$sum": "$counter_volume"}
            }
        },
    ])

    return cumulative_data, gauge_data, delta_data


def save_ceilometer_usages(
    cumulative_data,
    gauge_data,
    delta_data,
    date,
    warehouse
):
    new = total = 0
    for item in chain(cumulative_data, gauge_data, delta_data):
        tenant_id = item['_id']['project_id']
        flavor_name = item['_id']['counter_name']
        value = item['value']
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
            value=value,  # ceilometer usages are saved each 10 minutes
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
def openstack_mongo_ceilometer(today, **kwargs):
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
        cumulative_data, gauge_data, delta_data = get_ceilometer_usages(
            today, site['CEILOMETER_CONNECTION']
        )
        site_new, site_total = save_ceilometer_usages(
            cumulative_data['result'],
            gauge_data['result'],
            delta_data['result'],
            today,
            warehouse)

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

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime
from decimal import Decimal as D

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import IntegrityError
from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_scrooge.models import (
    AssetInfo,
    DailyUsage,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    UsagePrice,
    UsageType,
    Warehouse,
)
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


def get_asset_info(service_environment, warehouse, data):
    """
    Update AssetInfo object or create it if not exist.

    :param object service_environment: Django ORM ServiceEnvironment object
    :param object warehouse: Django ORM Warehouse object
    :param dict data: Data from Ralph 3 REST API
    :returns list: AssetInfo PricingObject and status
    :rtype:
    """
    created = False
    try:
        asset_info = AssetInfo.objects.get(ralph3_asset_id=data['id'])
    except AssetInfo.DoesNotExist:
        asset_info = AssetInfo(
            ralph3_asset_id=data['id'],
            type_id=PRICING_OBJECT_TYPES.ASSET,
        )
        created = True
    asset_info.service_environment = service_environment
    asset_info.name = data['hostname']
    asset_info.warehouse = warehouse
    asset_info.sn = data['sn']
    asset_info.barcode = data['barcode']
    try:
        asset_info.save()
    except IntegrityError:
        # check for duplicates on SN, barcode and id, null them and save again
        for field in ['sn', 'barcode']:
            if data[field] is None:
                continue
            assets = AssetInfo.objects.filter(**{field: data[field]}).exclude(
                ralph3_asset_id=data['id'],
            )
            for asset in assets:
                logger.error('Duplicated {} ({}) on assets {} and {}'.format(
                    field,
                    data[field],
                    data['id'],
                    asset.ralph3_asset_id,
                ))
                setattr(asset, field, None)
                asset.save()
        asset_info.save()

    return asset_info, created


# TODO(xor-xor): Since there's such method on DataCenterAsset model in Ralph,
# we need to think about exposing it as some "special" endpoint in API. But by
# that time, we will use this function below (copied from ralph_assets, with
# slight modifications, but the logic is exactly the same).
def _is_depreciated(data, date):

    def get_depreciation_months(data):
        depreciation_rate = float(data['depreciation_rate'])
        return int(
            (1 / (depreciation_rate / 100) * 12)
            if depreciation_rate else 0
        )

    def d(date):
        return datetime.strptime(date, "%Y-%m-%d").date()

    date = date or datetime.date.today()
    if data['force_depreciation'] or not data['invoice_date']:
        return True
    if data['depreciation_end_date']:
        depreciation_date = d(data['depreciation_end_date'])
    else:
        depreciation_date = d(data['invoice_date']) + relativedelta(
            months=get_depreciation_months(data),
        )
    return depreciation_date < date


def get_daily_asset_info(asset_info, date, data):
    """
    Get or create daily asset info

    :param object asset_info: Django ORM AssetInfo object
    :param object date: datetime
    :param dict data: Data from assets API
    :returns list: Django ORM DailyAssetInfo object
    :rtype:
    """
    daily_asset_info = asset_info.get_daily_pricing_object(date)
    daily_asset_info.depreciation_rate = data['depreciation_rate']
    daily_asset_info.is_depreciated = _is_depreciated(data, date)
    daily_asset_info.price = data['price'] or 0
    daily_asset_info.save()
    return daily_asset_info


def update_usage(daily_asset_info, warehouse, usage_type, value, date):
    """
    Updates (or creates) usage of given usage_type for device.

    :param object daily_asset_info: Django ORM DailyAssetInfo object
    :param object warehouse: Django ORM Warehouse object
    :param object usage_type: Django ORM UsageType object
    :param object value: value from asset api for given usage type  # XXX what?
    :param object date: datetime
    """
    defaults = dict(
        service_environment=daily_asset_info.service_environment,
        warehouse=warehouse,
    )
    usage, usage_created = DailyUsage.objects.get_or_create(
        date=date,
        type=usage_type,
        daily_pricing_object=daily_asset_info,
        defaults=defaults
    )
    # set defaults if daily usage was not created
    if not usage_created:
        for attr, value in defaults.iteritems():
            setattr(usage, attr, value)
    usage.value = value
    usage.save()


# TODO(xor-xor): Rename 'data' to some more descriptive variable name.
@commit_on_success
def update_asset(data, date, usages, unknown_service_env):
    """
    Updates single asset.

    Creates asset if not exists, then creates its daily snapshot.

    When asset has no service-env, unknown is used.
    When asset has no data center assigned, default (from fixtures) is used.

    :param dict data: Data from assets API
    :param object date: datetime
    :param dict usages: Dict with usage types from Django ORM UsageType
    :returns: True, if asset info was created, else False
    :rtype boolean:
    """
    dc_asset_repr = data['__str__']
    if data.get('service_env') is None:
        service_environment = unknown_service_env
        logger.warning(
            'Missing service environment for DC Asset {}'.format(dc_asset_repr)
        )
    else:
        try:
            service_environment = ServiceEnvironment.objects.get(
                environment__name=data['service_env']['environment'],
                service__ci_uid=data['service_env']['service_uid']
            )
        except ServiceEnvironment.DoesNotExist:
            service_environment = unknown_service_env
            logger.warning(
                'Invalid service environment for DC Asset {}: {} - {}'.format(
                    dc_asset_repr, data['service_env']['service_uid'],
                    data['service_env']['environment']
                )
            )

    if (
        data.get('rack') is None or
        data['rack'].get('server_room') is None or
        data['rack']['server_room'].get('data_center') is None
    ):
        warehouse = Warehouse.objects.get(pk=1)  # Default one from fixtures
        logger.warning('Missing rack for DC Asset {}'.format(dc_asset_repr))
    else:
        try:
            dc_id = data['rack']['server_room']['data_center']['id']
            warehouse = Warehouse.objects.get(ralph3_id=dc_id)
        except Warehouse.DoesNotExist:
            warehouse = Warehouse.objects.get(pk=1)  # Default from fixtures
            logger.warning('Invalid data center for {}: {}'.format(
                dc_asset_repr, data['rack']['server_room']['data_center']['id']
            ))
    asset_info, asset_info_created = get_asset_info(
        service_environment,
        warehouse,
        data,
    )
    daily_asset_info = get_daily_asset_info(
        asset_info,
        date,
        data,
    )

    update_usage(
        daily_asset_info,
        warehouse,
        usages['depreciation'],
        daily_asset_info.daily_cost,
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['assets_count'],
        1,
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['cores_count'],
        data['model']['cores_count'],
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['power_consumption'],
        data['model']['power_consumption'],
        date,
    )
    update_usage(
        daily_asset_info,
        warehouse,
        usages['collocation'],
        data['model']['height_of_device'],
        date,
    )
    logger.info('Successfully saved {}'.format(dc_asset_repr))
    return asset_info_created


def get_usage(symbol, name, by_warehouse, by_cost, average, type):
    """
    Creates power consumption usage type if not created.

    :param string symbol: Symbol name
    :param string name: Usage type name
    :param boolean by_warehouse: Flag by_warehouse
    :param boolean by_cost: Flag by_cost
    :param boolean average: Flag average
    :param str type: Type of UsageType (see UsageType.TYPE_CHOICES for details)
    :returns object: Django ORM UsageType object
    :rtype object:
    """
    usage_type, created = UsageType.objects_admin.get_or_create(
        symbol=symbol,
        defaults=dict(
            name=name,
            by_warehouse=by_warehouse,
            by_cost=by_cost,
            average=average,
        ),
    )
    usage_type.usage_type = type
    usage_type.save()
    return usage_type


def get_unknown_service_env():
    service_uid, env_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'ralph3_asset', (None, None)
    )
    unknown_service_env = None
    if service_uid:
        try:
            unknown_service_env = ServiceEnvironment.objects.get(
                service__ci_uid=service_uid,
                environment__name=env_name,
            )
        except ServiceEnvironment.DoesNotExist:
            pass
    if not unknown_service_env:
        raise UnknownServiceEnvironmentNotConfiguredError()
    return unknown_service_env


@plugin.register(
    chain='scrooge',
    requires=[
        'ralph3_service_environment',
        'ralph3_data_center',
        'ralph3_asset_model'
    ]
)
def ralph3_asset(**kwargs):
    """
    Updates assets and usages

    :returns tuple: Plugin status and statistics
    :rtype tuple:
    """
    date = kwargs['today']
    depreciation_usage = get_usage(
        'depreciation',
        'Depreciation',
        by_warehouse=False,
        by_cost=False,
        average=True,
        type='BU',
    )
    try:
        usage_price = UsagePrice.objects.get(
            type=depreciation_usage
        )
    except UsagePrice.DoesNotExist:
        usage_price = UsagePrice(type=depreciation_usage)
    usage_price.start = date.min
    usage_price.end = date.max
    usage_price.price = D('1')
    usage_price.forecast_price = D('1')
    usage_price.save()

    try:
        unknown_service_env = get_unknown_service_env()
    except UnknownServiceEnvironmentNotConfiguredError:
        msg = 'Unknown service environment not configured for "asset"'
        logger.error(msg)
        return (False, msg)

    usages = {
        'depreciation': depreciation_usage,
        'assets_count': get_usage(
            'assets_count',
            'Assets Count',
            by_warehouse=False,
            by_cost=False,
            average=True,
            type='SU',
        ),
        'cores_count': get_usage(
            'physical_cpu_cores',
            'Physical CPU cores count',
            by_warehouse=False,
            by_cost=False,
            average=True,
            type='SU',
        ),
        'power_consumption': get_usage(
            'power_consumption',
            'Power consumption',
            by_warehouse=True,
            by_cost=True,
            average=False,
            type='BU',
        ),
        'collocation': get_usage(
            'collocation',
            'Collocation',
            by_warehouse=True,
            by_cost=True,
            average=True,
            type='BU',
        ),
    }

    new = update = total = 0
    queries = (
        "invoice_date__isnull=True",
        "invoice_date__lt={}".format(date.isoformat()),
    )
    for data in get_combined_data(queries):
        total += 1
        created = update_asset(data, date, usages, unknown_service_env)
        if created:
            new += 1
        else:
            update += 1

    return True, '{} new assets, {} updated, {} total'.format(
        new, update, total
    )


def get_combined_data(queries):
    """
    Generates (chain) data from multiple queries to Ralph3. Each row is
    validated (if Scrooge should handle this asset or not).
    """
    for query in queries:
        for asset in get_from_ralph("data-center-assets", logger, query=query):
            if validate_asset(asset):
                yield asset


# Heavily stripped down version of ralph_assets.api_scrooge.get_assets.
def validate_asset(asset):
    """
    Check if asset should be handled by Scrooge.

    Returns True if it should, False otherwise.
    """
    if asset['status'] == 'liquidated':
        logger.info(
            "Skipping DataCenterAsset {} - it's liquidated".format(
                asset['__str__']
            )
        )
        return False
    return True

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin, api_scrooge
from ralph_scrooge.models import (
    AssetInfo,
    DatabaseInfo,
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
)

from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)

logger = logging.getLogger(__name__)


def get_database_model(ralph_database):
    model, created = PricingObjectModel.objects.get_or_create(
        model_id=ralph_database['type_id'],
        type_id=PRICING_OBJECT_TYPES.DATABASE,
        defaults=dict(
            name=ralph_database['type'],
        )
    )
    model.name = ralph_database['type']
    model.save()
    return model


def save_database_info(ralph_database, unknown_service_environment):
    created = False
    try:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_id=ralph_database['service_id'],
            environment__ci_id=ralph_database['environment_id'],
        )
    except ServiceEnvironment.DoesNotExist:
        logger.warning(
            'Invalid / missing service environment for Database {}-{}'.format(
                ralph_database['parent_device_id'],
                ralph_database['name']
            )
        )
        service_environment = unknown_service_environment

    try:
        database_info = DatabaseInfo.objects.get(
            database_id=ralph_database['database_id'],
        )
    except DatabaseInfo.DoesNotExist:
        created = True
        database_info = DatabaseInfo(
            database_id=ralph_database['database_id'],
            type_id=PRICING_OBJECT_TYPES.DATABASE,
        )

    try:
        parent_device = AssetInfo.objects.get(
            device_id=ralph_database['parent_device_id']
        )
    except AssetInfo.DoesNotExist:
        parent_device = None

    database_info.model = get_database_model(ralph_database)
    database_info.name = ralph_database['name']
    database_info.parent_device = parent_device
    database_info.service_environment = service_environment
    database_info.save()
    return created, database_info


def save_daily_database_info(ralph_database, database_info, date):
    daily_database_info = database_info.get_daily_pricing_object(date)
    daily_parent = None
    if database_info.parent_device:
        daily_parent = database_info.parent_device.get_daily_pricing_object(
            date
        )
    daily_database_info.service_environment = database_info.service_environment
    daily_database_info.parent_device = daily_parent
    daily_database_info.save()
    return daily_database_info


def update_database(ralph_database, date, unknown_service_environment):
    """
    Updates single database info
    """
    created, database_info = save_database_info(
        ralph_database,
        unknown_service_environment,
    )
    save_daily_database_info(ralph_database, database_info, date)
    return created


def get_unknown_service_environment(model_name):
    """
    Returns unknown service environment for database
    """
    service_uid, environment_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'database', {}
    ).get(model_name, (None, None))
    unknown_service_environment = None
    if service_uid:
        try:
            unknown_service_environment = ServiceEnvironment.objects.get(
                service__ci_uid=service_uid,
                environment__name=environment_name,
            )
        except ServiceEnvironment.DoesNotExist:
            pass
    if not unknown_service_environment:
        raise UnknownServiceEnvironmentNotConfiguredError()
    return unknown_service_environment


@plugin.register(chain='scrooge', requires=['service', 'asset'])
def database(today, **kwargs):
    new = total = 0
    for database_type in settings.DATABASE_TYPES:
        # check if unknown service environment is configured
        try:
            unknown_service_environment = get_unknown_service_environment(
                database_type
            )
        except UnknownServiceEnvironmentNotConfiguredError:
            logger.error(
                'Unknown service environment not configured for {}'.format(
                    database_type
                )
            )
        else:
            for ralph_database in api_scrooge.get_databases(
                database_type=database_type
            ):
                total += 1
                if update_database(
                    ralph_database,
                    today,
                    unknown_service_environment,
                ):
                    new += 1
    return True, 'Databases: {0} new, {1} updated, {2} total'.format(
        new,
        total - new,
        total,
    )

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin
from ralph_scrooge.models import (
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    TenantInfo,
)
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


def save_tenant_info(ralph_tenant, unknown_service_env):
    created = False
    try:
        service_environment = ServiceEnvironment.objects.get(
            # XXX should we get service env by service_id && env_id..?
            id=ralph_tenant['service_env']['id']  # XXX what if service env will be empty?
        )
    except ServiceEnvironment.DoesNotExist:
        logger.warning(
            'Invalid (or missing) service environment for project {}'.format(
                ralph_tenant['name']
            )
        )
        service_environment = unknown_service_env

    try:
        tenant_info = TenantInfo.objects.get(
            tenant_id=ralph_tenant['id'],
        )
    except TenantInfo.DoesNotExist:
        created = True
        tenant_info = TenantInfo(
            tenant_id=ralph_tenant['id'],
            type_id=PRICING_OBJECT_TYPES.TENANT,
        )
    tenant_info.name = ralph_tenant['name']
    tenant_info.remarks = ralph_tenant['remarks']
    tenant_info.service_environment = service_environment
    tenant_info.save()
    return created, tenant_info


def save_daily_tenant_info(ralph_tenant, tenant_info, date):
    daily_tenant_info = tenant_info.get_daily_pricing_object(date)
    daily_tenant_info.service_environment = tenant_info.service_environment
    daily_tenant_info.save()
    return daily_tenant_info


def update_tenant(ralph_tenant, date, unknown_service_env):
    created, tenant_info = save_tenant_info(
        ralph_tenant,
        unknown_service_env,
    )
    save_daily_tenant_info(ralph_tenant, tenant_info, date)
    return created


def get_unknown_service_env():
    service_uid, env_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'tenant', (None, None)
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


# XXX rename tenant to project..?
@plugin.register(chain='scrooge', requires=['service'])
def tenant(today, **kwargs):
    new = total = 0
    try:
        unknown_service_env = get_unknown_service_env()
    except UnknownServiceEnvironmentNotConfiguredError:
        msg = 'Unknown service environment not configured for "tenant"'
        logger.error(msg)
        return (False, msg)

    for provider in get_from_ralph("cloud-providers", logger):
        if provider['name'].lower() == "openstack":
            provider_id = provider['id']
    if provider_id is None:
        msg = "Can't find cloud provider for OpenStack in Ralph"
        logger.error(msg)
        return (False, msg)

    query = "cloudprovider={}".format(provider_id)
    for ralph_tenant in get_from_ralph("cloud-projects", logger, query=query):
        created = update_tenant(ralph_tenant, today, unknown_service_env)
        if created:
            new += 1
        total += 1
    return True, '{} new tenants, {} updated, {} total'.format(
        new,
        total - new,
        total,
    )

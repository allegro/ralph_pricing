# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph_scrooge.models import (
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    # TODO(xor-xor): TenantInfo should be renamed to CloudProjectInfo.
    # This also applies to every occurrence of word 'tenant' in this plugin
    # (i.e., 'tenant' -> 'cloud_project').
    TenantInfo,
)
from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


def save_tenant_info(ralph_tenant, unknown_service_env):
    created = False
    if ralph_tenant.get('service_env') is None:
        logger.warning(
            'Invalid (or missing) service environment in Ralph '
            'for project {} ({})'.format(
                ralph_tenant['name'],
                ralph_tenant['project_id']
            )
        )
        service_environment = unknown_service_env
    else:
        try:
            service_environment = ServiceEnvironment.objects.get(
                environment__name=ralph_tenant['service_env']['environment'],
                service__ci_uid=ralph_tenant['service_env']['service_uid']
            )
        except ServiceEnvironment.DoesNotExist:
            logger.warning(
                'Invalid (or missing) service environment in Scrooge '
                'for project {}'.format(ralph_tenant['name'])
            )
            service_environment = unknown_service_env
    try:
        tenant_info = TenantInfo.objects.get(
            ralph3_tenant_id=ralph_tenant['id'],
        )
    except TenantInfo.DoesNotExist:
        # try to get tenant by its id in cloud provider
        try:
            tenant_info = TenantInfo.objects.get(
                tenant_id=ralph_tenant['project_id']
            )
        except TenantInfo.DoesNotExist:
            created = True
            tenant_info = TenantInfo(
                ralph3_tenant_id=ralph_tenant['id'],
                type_id=PRICING_OBJECT_TYPES.TENANT,
            )
    tenant_info.ralph3_tenant_id = ralph_tenant['id']
    tenant_info.name = ralph_tenant['name']
    tenant_info.remarks = ralph_tenant['remarks']
    tenant_info.tenant_id = ralph_tenant['project_id']
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
        'ralph3_tenant', (None, None)
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


@plugin_runner.register(
    chain='scrooge', requires=['ralph3_service_environment']
)
def ralph3_cloud_project(today, **kwargs):
    new = total = 0
    try:
        unknown_service_env = get_unknown_service_env()
    except UnknownServiceEnvironmentNotConfiguredError:
        msg = 'Unknown service environment not configured for "tenant"'
        logger.error(msg)
        return (False, msg)

    for provider in get_from_ralph("cloud-providers", logger):
        logger.info('Processing cloud provider {}'.format(provider['name']))
        provider_id = provider['id']
        query = "cloudprovider={}".format(provider_id)
        for ralph_tenant in get_from_ralph(
            "cloud-projects", logger, query=query
        ):
            created = update_tenant(ralph_tenant, today, unknown_service_env)
            if created:
                new += 1
            total += 1
    return True, '{} new tenants, {} updated, {} total'.format(
        new,
        total - new,
        total,
    )

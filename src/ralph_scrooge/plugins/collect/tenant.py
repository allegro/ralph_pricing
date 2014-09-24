# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin, api_scrooge
from ralph_scrooge.models import (
    DailyTenantInfo,
    PricingObjectType,
    ServiceEnvironment,
    TenantGroup,
    TenantInfo,
)


logger = logging.getLogger(__name__)


class UnknownServiceEnvironmentNotConfiguredError(Exception):
    pass


def get_tenant_group(tenant):
    tenant_group = TenantGroup.objects.get_or_create(
        group_id=tenant['model_id'],
        defaults=dict(
            name=tenant['model_name'],
        )
    )[0]
    tenant_group.name = tenant['model_name']
    tenant_group.save()
    return tenant_group


def save_tenant_info(tenant, unknown_service_environment):
    created = False
    try:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_id=tenant['service_id'],
            environment__ci_id=tenant['environment_id'],
        )
    except ServiceEnvironment.DoesNotExist:
        logger.warning(
            'Invalid (or missing) service environment for tenant {}-{}'.format(
                tenant['device_id'],
                tenant['name']
            )
        )
        service_environment = unknown_service_environment

    try:
        tenant_info = TenantInfo.objects.get(tenant_id=tenant['tenant_id'])
    except TenantInfo.DoesNotExist:
        created = True
        tenant_info = TenantInfo(
            tenant_id=tenant['tenant_id'],
            type=PricingObjectType.tenant,
        )
    tenant_info.group = get_tenant_group(tenant)
    tenant_info.name = tenant['name']
    tenant_info.remarks = tenant['remarks']
    tenant_info.device_id = tenant['device_id']
    tenant_info.service_environment = service_environment
    tenant_info.save()
    return created, tenant_info


def save_daily_tenant_info(tenant, tenant_info, date):
    daily_tenant_info, created = DailyTenantInfo.objects.get_or_create(
        tenant_info=tenant_info,
        pricing_object=tenant_info,
        date=date,
        defaults=dict(
            service_environment=tenant_info.service_environment,
        )
    )
    daily_tenant_info.service_environment = tenant_info.service_environment
    daily_tenant_info.save()
    return daily_tenant_info


def update_tenant(tenant, date, unknown_service_environment):
    """
    Updates single tenant info
    """
    created, tenant_info = save_tenant_info(
        tenant,
        unknown_service_environment,
    )
    save_daily_tenant_info(tenant, tenant_info, date)
    return created


def get_tenant_unknown_service_environment():
    """
    Returns unknown service environment for OpenStack tenants
    """
    service_uid, environment_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'tenant'
    )
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


@plugin.register(chain='scrooge', requires=['service'])
def tenant(today, **kwargs):
    try:
        unknown_service_environment = get_tenant_unknown_service_environment()
    except UnknownServiceEnvironmentNotConfiguredError:
        return (
            False,
            'Unknown service environment not configured for tenant plugin'
        )

    new = total = 0
    for tenant in api_scrooge.get_openstack_tenants():
        total += 1
        if update_tenant(
            tenant,
            today,
            unknown_service_environment,
        ):
            new += 1
    return True, 'Tenants: {0} new, {1} updated, {2} total'.format(
        new,
        total - new,
        total,
    )

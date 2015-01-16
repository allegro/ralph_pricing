# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings

from ralph.util import plugin, api_scrooge
from ralph_scrooge.models import (
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    TenantInfo,
)
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)

logger = logging.getLogger(__name__)


def get_model(ralph_tenant):
    model = PricingObjectModel.objects.get_or_create(
        model_id=ralph_tenant['model_id'],
        type_id=PRICING_OBJECT_TYPES.TENANT,
        defaults=dict(
            name=ralph_tenant['model_name'],
        )
    )[0]
    model.name = ralph_tenant['model_name']
    model.save()
    return model


def save_tenant_info(ralph_tenant, unknown_service_environment):
    created = False
    try:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_id=ralph_tenant['service_id'],
            environment__ci_id=ralph_tenant['environment_id'],
        )
    except ServiceEnvironment.DoesNotExist:
        logger.warning(
            'Invalid (or missing) service environment for tenant {}-{}'.format(
                ralph_tenant['device_id'],
                ralph_tenant['name']
            )
        )
        service_environment = unknown_service_environment

    try:
        tenant_info = TenantInfo.objects.get(
            tenant_id=ralph_tenant['tenant_id'],
        )
    except TenantInfo.DoesNotExist:
        created = True
        tenant_info = TenantInfo(
            tenant_id=ralph_tenant['tenant_id'],
            type_id=PRICING_OBJECT_TYPES.TENANT,
        )
    tenant_info.model = get_model(ralph_tenant)
    tenant_info.name = ralph_tenant['name']
    tenant_info.remarks = ralph_tenant['remarks']
    tenant_info.device_id = ralph_tenant['device_id']
    tenant_info.service_environment = service_environment
    tenant_info.save()
    return created, tenant_info


def save_daily_tenant_info(ralph_tenant, tenant_info, date):
    daily_tenant_info = tenant_info.get_daily_pricing_object(date)
    daily_tenant_info.service_environment = tenant_info.service_environment
    daily_tenant_info.save()
    return daily_tenant_info


def update_tenant(ralph_tenant, date, unknown_service_environment):
    """
    Updates single tenant info
    """
    created, tenant_info = save_tenant_info(
        ralph_tenant,
        unknown_service_environment,
    )
    save_daily_tenant_info(ralph_tenant, tenant_info, date)
    return created


def get_unknown_service_environment(model_name):
    """
    Returns unknown service environment for OpenStack tenants
    """
    service_uid, environment_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'tenant', {}
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


@plugin.register(chain='scrooge', requires=['service'])
def tenant(today, **kwargs):
    new = total = 0
    # check if all unknown SE are configured
    for openstack_model in settings.OPENSTACK_TENANTS_MODELS:
        try:
            unknown_service_environment = get_unknown_service_environment(
                openstack_model
            )
        except UnknownServiceEnvironmentNotConfiguredError:
            msg = 'Unknown service environment not configured for {}'.format(
                openstack_model
            )
            logger.error(msg)
            return (False, msg)

    for openstack_model in settings.OPENSTACK_TENANTS_MODELS:
        unknown_service_environment = get_unknown_service_environment(
            openstack_model
        )
        for ralph_tenant in api_scrooge.get_openstack_tenants(openstack_model):
            total += 1
            if update_tenant(
                ralph_tenant,
                today,
                unknown_service_environment,
            ):
                new += 1
    return True, 'Tenants: {0} new, {1} updated, {2} total'.format(
        new,
        total - new,
        total,
    )

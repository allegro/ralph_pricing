# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings
from keystoneclient.v2_0 import client

from ralph.util import plugin
from ralph_scrooge.models import (
    DailyTenantInfo,
    PricingObjectType,
    ServiceEnvironment,
    TenantInfo,
)


logger = logging.getLogger(__name__)


class InvalidTenantServiceEnvironment(Exception):
    pass


class UnknownServiceEnvironmentNotConfigured(Exception):
    pass


def get_tenant_service_environment(tenant):
    try:
        # TODO: change to symbol
        service_name = getattr(
            tenant,
            settings.OPENSTACK_TENANT_SERVICE_FIELD or ''
        )
        # TODO: change to symbol
        environment_name = getattr(
            tenant,
            settings.OPENSTACK_TENANT_ENVIRONMENT_FIELD or ''
        )
        return ServiceEnvironment.objects.get(
            service__name=service_name,
            environment__name=environment_name,
        )
    except (AttributeError, ServiceEnvironment.DoesNotExist) as e:
        raise InvalidTenantServiceEnvironment(e)


def save_tenant_info(tenant, unknown_service_environment):
    created = False
    try:
        service_environment = get_tenant_service_environment(tenant)
    except InvalidTenantServiceEnvironment:
        logger.warning(
            'Invalid (or missing) service environment for tenant {}'.format(
                tenant.name
            )
        )
        service_environment = unknown_service_environment

    try:
        tenant_info = TenantInfo.objects.get(tenant_id=tenant.id)
    except TenantInfo.DoesNotExist:
        created = True
        tenant_info = TenantInfo(
            tenant_id=tenant.id,
            type=PricingObjectType.tenant,
        )
    tenant_info.name = tenant.name
    tenant_info.remarks = tenant.description or ''
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
    daily_tenant_info.enabled = tenant.enabled
    daily_tenant_info.save()
    return daily_tenant_info


def update_tenant(tenant, date, unknown_service, unknown_environment):
    """
    Updates single tenant info
    """
    created, tenant_info = save_tenant_info(
        tenant,
        unknown_service,
        unknown_environment,
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
        raise UnknownServiceEnvironmentNotConfigured()
    return unknown_service_environment


def get_tenants_list(site):
    """
    Returns list of tenants from OpenStack
    """
    keystone_client = client.Client(
        username=site['OS_USERNAME'],
        password=site['OS_PASSWORD'],
        tenant_name=site['OS_TENANT_NAME'],
        auth_url=site['OS_AUTH_URL'],
    )
    return keystone_client.tenants.list()


@plugin.register(chain='scrooge', requires=['service'])
def tenant(today, **kwargs):
    """
    Pricing plugin for openstack havana- ceilometer.
    """
    if not settings.OPENSTACK_TENANT_SERVICE_FIELD:
        return False, 'Tenant service field not configured'

    if not settings.OPENSTACK_TENANT_ENVIRONMENT_FIELD:
        return False, 'Tenant environment field not configured'

    try:
        unknown_service_environment = get_tenant_unknown_service_environment()
    except UnknownServiceEnvironmentNotConfigured:
        return (
            False,
            'Unknown service environment not configured for tenant plugin'
        )

    new = total = 0
    for site in settings.OPENSTACK_SITES:
        site_new = site_total = 0
        logger.info("OpenStack site {}".format(site['OS_METERING_URL']))
        tenants = get_tenants_list(site)
        site_total = len(tenants)
        for tenant in tenants:
            if update_tenant(
                tenant,
                today,
                unknown_service_environment,
            ):
                site_new += 1
        logger.info('{} new, {} total tenants saved for site {}'.format(
            site_new,
            site_total,
            site['OS_METERING_URL'],
        ))
        new += site_new
        total += site_total

    return True, 'Tenants: {0} new, {1} updated, {2} total'.format(
        new,
        total - new,
        total,
    )

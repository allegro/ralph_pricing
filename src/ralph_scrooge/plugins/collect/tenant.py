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
    Environment,
    PricingObjectType,
    Service,
    TenantInfo,
)


logger = logging.getLogger(__name__)


class InvalidTenantService(Exception):
    pass


class InvalidTenantEnvironment(Exception):
    pass


class UnknownServiceNotConfigured(Exception):
    pass


class UnknownEnvironmentNotConfigured(Exception):
    pass


def get_tenant_service(tenant):
    try:
        service_symbol = getattr(
            tenant,
            settings.OPENSTACK_TENANT_SERVICE_FIELD or ''
        )
        # TODO: change to symbol
        return Service.objects.get(name=service_symbol)
    except (AttributeError, Service.DoesNotExist) as e:
        raise InvalidTenantService(e)


def get_tenant_environment(tenant):
    try:
        environment_symbol = getattr(
            tenant,
            settings.OPENSTACK_TENANT_ENVIRONMENT_FIELD or ''
        )
        return Environment.objects.get(name=environment_symbol)
    except (AttributeError, Environment.DoesNotExist) as e:
        raise InvalidTenantEnvironment(e)


def save_tenant_info(tenant, unknown_service, unknown_environment):
    created = False
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
    try:
        service = get_tenant_service(tenant)
    except InvalidTenantService:
        logger.warning('Invalid (or missing) service for tenant {}'.format(
            tenant.name
        ))
        service = unknown_service
    try:
        environment = get_tenant_environment(tenant)
    except InvalidTenantEnvironment:
        logger.warning('Invalid (or missing) environment for tenant {}'.format(
            tenant.name
        ))
        environment = unknown_environment
    tenant_info.service = service
    tenant_info.environment = environment
    tenant_info.save()
    return created, tenant_info


def save_daily_tenant_info(tenant, tenant_info, date):
    defaults = dict(
        service=tenant_info.service,
        environment=tenant_info.environment,
    )
    daily_tenant_info, created = DailyTenantInfo.objects.get_or_create(
        tenant_info=tenant_info,
        pricing_object=tenant_info,
        date=date,
        defaults=defaults
    )
    # set defaults if daily tenant was not created
    if not created:
        for attr, value in defaults.iteritems():
            setattr(daily_tenant_info, attr, value)
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


def get_tenant_unknown_service():
    """
    Returns unknown service for OpenStack tenants
    """
    unknown_service_uid = settings.UNKNOWN_SERVICES.get('tenant')
    unknown_service = None
    if unknown_service_uid:
        try:
            unknown_service = Service.objects.get(
                ci_uid=unknown_service_uid
            )
        except Service.DoesNotExist:
            pass
    if not unknown_service:
        raise UnknownServiceNotConfigured()
    return unknown_service


def get_tenant_unknown_environment():
    """
    Returns unknown environment for OpenStack tenants
    """
    unknown_environment_name = settings.UNKNOWN_ENVIRONMENTS.get('tenant')
    unknown_environment = None
    if unknown_environment_name:
        try:
            unknown_environment = Environment.objects.get(
                name=unknown_environment_name,
            )
        except Environment.DoesNotExist:
            pass
    if not unknown_environment:
        raise UnknownEnvironmentNotConfigured()
    return unknown_environment


def get_tenants_list(site):
    """
    Returns list of tenants from OpenStack
    """
    ks = client.Client(
        username=site['OS_USERNAME'],
        password=site['OS_PASSWORD'],
        tenant_name=site['OS_TENANT_NAME'],
        auth_url=site['OS_AUTH_URL'],
    )
    return ks.tenants.list()


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
        unknown_service = get_tenant_unknown_service()
    except UnknownServiceNotConfigured:
        return False, 'Unknown service not configured for tenant plugin'

    try:
        unknown_environment = get_tenant_unknown_environment()
    except UnknownEnvironmentNotConfigured:
        return False, 'Unknown environment not configured for tenant plugin'

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
                unknown_service,
                unknown_environment
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

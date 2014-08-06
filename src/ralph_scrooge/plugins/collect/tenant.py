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
    Service,
    TenantInfo,
)


logger = logging.getLogger(__name__)


class InvalidTenantService(Exception):
    pass


class UnknownServiceNotConfigured(Exception):
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


def save_tenant_info(tenant, unknown_service):
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
    tenant_info.service = service
    tenant_info.save()
    return created, tenant_info


def save_daily_tenant_info(tenant, tenant_info, date):
    daily_tenant_info, created = DailyTenantInfo.objects.get_or_create(
        tenant_info=tenant_info,
        pricing_object=tenant_info,
        date=date,
        defaults=dict(
            service=tenant_info.service,
        )
    )
    daily_tenant_info.service = tenant_info.service
    daily_tenant_info.enabled = tenant.enabled
    daily_tenant_info.save()
    return daily_tenant_info


def update_tenant(tenant, date, tenant_unknown_service):
    """
    Updates single tenant info
    """
    created, tenant_info = save_tenant_info(tenant, tenant_unknown_service)
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

    try:
        unknown_service = get_tenant_unknown_service()
    except UnknownServiceNotConfigured:
        return False, 'Unknown service not configured for tenant plugin'

    new = total = 0
    for site in settings.OPENSTACK_SITES:
        site_new = site_total = 0
        logger.info("OpenStack site {}".format(site['OS_METERING_URL']))
        tenants = get_tenants_list(site)
        site_total = len(tenants)
        for tenant in tenants:
            if update_tenant(tenant, today, unknown_service):
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

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
    PricingObject,
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
    ServiceEnvironment,
    VIPInfo,
)
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)


logger = logging.getLogger(__name__)


def get_vip_model(ralph_vip):
    model = PricingObjectModel.objects.get_or_create(
        model_id=ralph_vip['type_id'],
        type_id=PRICING_OBJECT_TYPES.VIP,
        defaults=dict(
            name=ralph_vip['type'],
        )
    )[0]
    model.name = ralph_vip['type']
    model.save()
    return model


def save_vip_info(ralph_vip, unknown_service_environment):
    created = False
    service_environment_found = False
    try:
        service_environment = ServiceEnvironment.objects.get(
            service__ci_id=ralph_vip['service_id'],
            environment__ci_id=ralph_vip['environment_id'],
        )
        service_environment_found = True
    except ServiceEnvironment.DoesNotExist:
        logger.warning(
            'Invalid (or missing) service environment for VIP {}-{}'.format(
                ralph_vip['device_id'],
                ralph_vip['name']
            )
        )
        service_environment = unknown_service_environment

    try:
        vip_info = VIPInfo.objects.get(
            vip_id=ralph_vip['vip_id'],
        )
    except VIPInfo.DoesNotExist:
        created = True
        vip_info = VIPInfo(
            vip_id=ralph_vip['vip_id'],
            type_id=PRICING_OBJECT_TYPES.VIP,
        )
    ip_info = PricingObject.objects.get_or_create(
        name=ralph_vip['ip_address'],
        type_id=PRICING_OBJECT_TYPES.IP_ADDRESS,
        defaults=dict(
            service_environment=service_environment,
        )
    )[0]

    if service_environment_found:
        ip_info.service_environment = service_environment
    ip_info.save()

    try:
        load_balancer = AssetInfo.objects.get(device_id=ralph_vip['device_id'])
    except AssetInfo.DoesNotExist:
        load_balancer = None

    vip_info.model = get_vip_model(ralph_vip)
    vip_info.name = ralph_vip['name']
    vip_info.port = ralph_vip['port']
    vip_info.ip_info = ip_info
    vip_info.load_balancer = load_balancer
    vip_info.service_environment = service_environment
    vip_info.save()
    return created, vip_info


def save_daily_vip_info(ralph_vip, vip_info, date):
    daily_vip_info = vip_info.get_daily_pricing_object(date)
    daily_vip_info.service_environment = vip_info.service_environment
    daily_vip_info.ip_info = vip_info.ip_info
    daily_vip_info.save()
    return daily_vip_info


def update_vip(ralph_vip, date, unknown_service_environment):
    """
    Updates single vip info
    """
    created, vip_info = save_vip_info(
        ralph_vip,
        unknown_service_environment,
    )
    save_daily_vip_info(ralph_vip, vip_info, date)
    return created


def get_unknown_service_environment(model_name):
    """
    Returns unknown service environment for VIP
    """
    service_uid, environment_name = settings.UNKNOWN_SERVICES_ENVIRONMENTS.get(
        'vip', {}
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
def vip(today, **kwargs):
    new = total = 0
    for vip_type in settings.VIP_TYPES:
        try:
            unknown_service_environment = get_unknown_service_environment(
                vip_type
            )
        except UnknownServiceEnvironmentNotConfiguredError:
            logger.error(
                'Unknown service environment not configured for {}'.format(
                    vip_type
                )
            )
        else:
            for ralph_vip in api_scrooge.get_vips(load_balancer_type=vip_type):
                total += 1
                if update_vip(
                    ralph_vip,
                    today,
                    unknown_service_environment,
                ):
                    new += 1
    return True, 'VIPs: {0} new, {1} updated, {2} total'.format(
        new,
        total - new,
        total,
    )

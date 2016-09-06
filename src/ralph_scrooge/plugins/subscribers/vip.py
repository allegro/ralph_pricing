# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging

from ralph_scrooge.models import (
    PRICING_OBJECT_TYPES,
    PricingObject,
    PricingObjectModel,
    ServiceEnvironment,
    VIPInfo,
)
from ralph_scrooge.plugins.collect._exceptions import (
    UnknownServiceEnvironmentNotConfiguredError,
)
from ralph_scrooge.plugins.collect.utils import get_unknown_service_env

from pyhermes.decorators import subscriber

logger = logging.getLogger(__name__)


def validate_vip_event_data(data):
    """Performs some basic sanity checks (e.g. missing values) on the incoming
    event data. Returns list of errors (if any).

    This function is copied from Ralph3 (data_center.subscribers), with slight
    modifications.
    """
    id = data['id']
    name = data['name']
    ip = data['ip']
    port = data['port']
    protocol = data['protocol']
    service = data['service']
    if service:
        service_uid = service.get('uid')
    else:
        service_uid = None
    environment = data['environment']
    lb_type = data['load_balancer_type']
    errors = []

    if not id:
        err = 'missing id'
        errors.append(err)
    if not name:
        err = 'missing name'
        errors.append(err)
    try:
        IPAddress(address=ip).clean_fields()
    except (TypeError, ValidationError):
        err = 'invalid IP address "{}"'.format(ip)
        errors.append(err)
    if not port or port < 1024 or port > 49151:
        err = 'invalid port "{}"'.format(port)
        errors.append(err)
    if not protocol:
        err = 'missing protocol'
        errors.append(err)
    if not service_uid:
        err = 'missing service UID'
        errors.append(err)
    if not environment:
        err = 'missing environment'
        errors.append(err)
    if not lb_type:
        err = 'missing load_balancer_type'
        errors.append(err)
    return errors


def normalize_lb_type(lb_type):
    # XXX(xor-xor): What about standarizing these names between external
    # systems and settings..?
    if lb_type == 'HAPROXY':
        return 'HA Proxy'
    else:
        return lb_type.upper()


def get_vip_model(event_data):
    lb_type = normalize_lb_type(event_data['load_balancer_type'])
    model = PricingObjectModel.objects.get_or_create(
        # model_id=event_data['type_id'],  # XXX we don't have anything like that in the incoming event_data
        name=lb_type,
        type_id=PRICING_OBJECT_TYPES.VIP,
    )[0]
    # XXX do we need to fill ralph3_model_id field here as well..?
    return model


def get_service_env(event_data):
    service_env_found = False
    try:
        service_env = ServiceEnvironment.objects.get(
            service__ci_uid=event_data['service']['uid'],
            environment__name=event_data['environment'],
        )
        service_env_found = True
    except ServiceEnvironment.DoesNotExist:
        msg = (
            'ServiceEnvironment for service UID "{}" and environment "{}" '
            'does not exist.'
        )
        logger.warning(
            msg.format(event_data['service']['uid'], event_data['environment'])
        )
    subtype = event_data['load_balancer_type']
    subtype = normalize_lb_type(subtype)
    service_env = get_unknown_service_env('vip', subtype=subtype)  # XXX use 'ralph3_vip' instead
    return (service_env, service_env_found)


def save_vip_info(event_data):
    service_env, service_env_found = get_service_env(event_data)
    try:
        vip_info = VIPInfo.objects.get(external_id=event_data['id'])
    except VIPInfo.DoesNotExist:
        # XXX @mkurek: there was a comment in old (Ralph2-based) vip plugin:
        # "TODO(?): check if there is single PricingObject with given name
        # first"
        # - is it still valid..?
        vip_info = VIPInfo(
            external_id=event_data['id'],
            type_id=PRICING_OBJECT_TYPES.VIP,
        )

    # get ip_info
    ip_info = PricingObject.objects.get_or_create(
        name=event_data['ip'],
        type_id=PRICING_OBJECT_TYPES.IP_ADDRESS,
        defaults=dict(service_environment=service_env)
    )[0]
    if service_env_found:
        ip_info.service_environment = service_env
    ip_info.save()

    # fill necessary vip_info fields and finally save it
    vip_info.model = get_vip_model(event_data)
    vip_info.name = event_data['name']
    vip_info.port = event_data['port']
    vip_info.ip_info = ip_info
    # We are temporarily null-ifying load_balancer field here, since there's no
    # ralph3_asset_id (or anything like that) in the incoming event_data (yet).
    vip_info.load_balancer = None
    vip_info.service_environment = service_env
    vip_info.save()
    return vip_info


def save_daily_vip_info(vip_info, date):
    daily_vip_info = vip_info.get_daily_pricing_object(date)
    daily_vip_info.service_environment = vip_info.service_environment
    daily_vip_info.ip_info = vip_info.ip_info
    daily_vip_info.save()
    return daily_vip_info


@subscriber(
    topic='refreshVipEvent',
)
def ralph3_vip(event_data):
    errors = validate_vip_event_data(event_data)
    if errors:
        msg = (
            'Error(s) detected in event data: {}. Ignoring received '
            'refreshVipEvent.'
        )
        logger.error(msg.format('; '.join(errors)))
        return

    # XXX @mkurek: since this plugin is not governed by plugin_runner, we have
    # lost the ability to pass an arbitrary date here - is this OK for you..?
    date = datetime.date.today()
    try:
        vip_info = save_vip_info(event_data)
    except UnknownServiceEnvironmentNotConfiguredError:
        msg = (
            'Unknown service environment not configured for "ralph3_vip" '
            'plugin'
        )
        logger.error(msg)
        return

    save_daily_vip_info(vip_info, date)

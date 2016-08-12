# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph_scrooge.models import (
    Environment,
    ProfitCenter,
    Owner,
    OwnershipType,
    Service,
    ServiceEnvironment,
    ServiceOwnership,
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


@commit_on_success
def update_service(service_from_ralph, default_profit_center):
    created = False
    try:
        service = Service.objects.get(ralph3_id=service_from_ralph['id'])
    except Service.DoesNotExist:
        service = Service(ralph3_id=service_from_ralph['id'])
        created = True
    service.name = service_from_ralph['name']
    service.symbol = service_from_ralph['uid']
    if service_from_ralph['profit_center'] is not None:
        service.profit_center = ProfitCenter.objects.get(
            ralph3_id=service_from_ralph['profit_center']['id']
        )
    else:
        service.profit_center = default_profit_center
    service.save()
    _update_owners(service, service_from_ralph)
    return created


def _delete_obsolete_owners(current, previous, service):
    to_delete = previous - current
    service.serviceownership_set.filter(
        owner__profile__user__username__in=to_delete
    ).delete()


def _add_new_owners(current, previous, service, owner_type):
    to_add = current - previous
    ownerships = []
    for owner in Owner.objects.filter(profile__user__username__in=to_add):
        so = ServiceOwnership(
            service=service,
            type=owner_type[1],
            owner=owner
        )
        ownerships.append(so)
    ServiceOwnership.objects.bulk_create(ownerships)


def _update_owners(service, service_from_ralph):
    owner_types = (
        ('technical_owners', OwnershipType.technical),
        ('business_owners', OwnershipType.business),
    )
    for owner_type in owner_types:
        # We get dicts from Ralph's API vs. objects from Scrooge's DB.
        current = set([
            owner['username'] for owner in service_from_ralph[owner_type[0]]
        ])
        previous = set(service.serviceownership_set.filter(
            type=owner_type[1]
        ).values_list('owner__profile__user__username', flat=True))
        _delete_obsolete_owners(current, previous, service)
        _add_new_owners(current, previous, service, owner_type)


@commit_on_success
def update_environment(env_from_ralph):
    env, created = Environment.objects.get_or_create(
        ralph3_id=env_from_ralph['id'],
    )
    env.name = env_from_ralph['name']
    env.save()
    return created


@plugin.register(chain='scrooge', requires=[])
def service_environment(**kwargs):
    new_services = total_services = 0
    new_envs = total_envs = 0
    new_service_envs = total_service_envs = 0

    if settings.SYNC_SERVICES_ONLY_CALCULATED_IN_SCROOGE:
        services_from_ralph = get_from_ralph(
            "services", logger, query="active=True"
        )
    else:
        services_from_ralph = get_from_ralph("services", logger)
    default_profit_center = ProfitCenter.objects.get(pk=1)

    # services
    for service in services_from_ralph:
        if update_service(service, default_profit_center):
            new_services += 1
        total_services += 1

    # envs
    for env in get_from_ralph("environments", logger):
        created = update_environment(env)
        if created:
            new_envs += 1
        total_envs += 1

    # service environments
    for service in services_from_ralph:
        service_obj = Service.objects.get(ralph3_id=service['id'])
        for env in service.get('environments', []):
            env_obj = Environment.objects.get(ralph3_id=env['id'])
            _, created = ServiceEnvironment.objects.get_or_create(
                service=service_obj,
                environment=env_obj,
            )
            if created:
                new_service_envs += 1
            total_service_envs += 1

    msg = ("; ".join([
        '{} new service(s), {} updated, {} total'.format(
            new_services,
            total_services - new_services,
            total_services,
        ),
        '{} new environment(s), {} updated, {} total'.format(
            new_envs,
            total_envs - new_envs,
            total_envs,
        ),
        '{} new service environment(s), {} updated, {} total'.format(
            new_service_envs,
            total_service_envs - new_service_envs,
            total_service_envs,
        ),
    ]))

    return True, msg

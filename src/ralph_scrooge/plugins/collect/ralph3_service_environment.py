# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db import transaction

from ralph_scrooge.models import (
    Environment,
    ProfitCenter,
    OwnershipType,
    Service,
    ScroogeUser,
    ServiceEnvironment,
    ServiceOwnership,
)
from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


@transaction.atomic
def update_service(
    service_from_ralph, default_profit_center, profit_centers, all_services
):
    created = False
    try:
        service = all_services[service_from_ralph['uid']]
    except KeyError:
        service = Service(ci_uid=service_from_ralph['uid'])
        created = True
    service.ralph3_id = service_from_ralph['id']
    service.name = service_from_ralph['name']
    service.symbol = service_from_ralph['uid']
    if service_from_ralph['profit_center'] is not None:
        service.profit_center = (
            profit_centers[service_from_ralph['profit_center']['id']]
        )
    else:
        service.profit_center = default_profit_center
    service.save()
    _update_owners(service, service_from_ralph)
    return created, service


def _delete_obsolete_owners(current, previous, service):
    to_delete = previous - current
    if to_delete:
        service.serviceownership_set.filter(
            owner__username__in=to_delete
        ).delete()


def _add_new_owners(current, previous, service, owner_type):
    to_add = current - previous
    ownerships = []
    if to_add:
        for owner in ScroogeUser.objects.filter(username__in=to_add):
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
        previous = set([
            su.owner.username
            for su in service.serviceownership_set.all()
            if su.type == owner_type[1]
        ])
        _delete_obsolete_owners(current, previous, service)
        _add_new_owners(current, previous, service, owner_type)


@transaction.atomic
def update_service_environments(service_obj, service_from_ralph, environments):
    created = total = 0
    existing_environments = set([
        e.name for e in service_obj.environments.all()
    ])
    for env in service_from_ralph.get('environments', []):
        if env['name'] not in existing_environments:
            _, created = ServiceEnvironment.objects.get_or_create(
                service=service_obj,
                environment=environments[env['name']],
            )
            if created:
                created += 1
            total += 1
    return created, total


@transaction.atomic
def update_environment(env_from_ralph):
    env, created = Environment.objects.get_or_create(
        name=env_from_ralph['name']
    )
    env.save()
    return created, env


@plugin_runner.register(chain='scrooge', requires=['ralph3_profit_center'])
def ralph3_service_environment(**kwargs):
    new_services = total_services = 0
    new_envs = total_envs = 0
    new_service_envs = total_service_envs = 0

    default_profit_center = ProfitCenter.objects.get(pk=1)  # from fixtures
    profit_centers = {
        pc.ralph3_id: pc for pc in ProfitCenter.objects.all()
    }

    # envs
    envs = {}
    for env in get_from_ralph("environments", logger):
        created, env_obj = update_environment(env)
        if created:
            new_envs += 1
        total_envs += 1
        envs[env['name']] = env_obj

    # services
    all_services = {
        s.ci_uid: s
        for s in Service.objects.prefetch_related(
            'serviceownership_set__owner',
            'environments'
        ).all()
    }

    for service in get_from_ralph(
        "services", logger, query="active=True"
    ):

        created, service_obj = update_service(
            service, default_profit_center, profit_centers, all_services
        )
        if created:
            new_services += 1
        total_services += 1

        created, total = update_service_environments(
            service_obj, service, envs
        )
        new_service_envs += created
        total_service_envs += total

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

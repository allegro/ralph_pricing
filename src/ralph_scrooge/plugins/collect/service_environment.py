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
        # XXX doesn't have get_or_create method..?
        service = Service.objects.get(ci_id=service_from_ralph['id'])
    except Service.DoesNotExist:
        service = Service(ci_id=service_from_ralph['id'])
        created = True
    service.name = service_from_ralph['name']
    service.symbol = service_from_ralph['uid']  # XXX confirm that symbol == uid
    if service_from_ralph['profit_center'] is not None:
        service.profit_center = ProfitCenter.objects.get(
            ci_id=service_from_ralph['profit_center']['id']
        )
    else:
        service.profit_center = default_profit_center
    service.save()
    _update_owners(service, service_from_ralph)
    return created


def _update_owners(service, service_from_ralph):

    owner_types = (
        ('technical_owners', OwnershipType.technical),
        ('business_owners', OwnershipType.business),
    )

    def delete_obsolete_owners():
        to_delete = previous_owners - current_owners
        service.serviceownership_set.filter(
            owner__cmdb_id__in=to_delete
        ).delete()

    def add_new_owners():
        to_add = current_owners - previous_owners
        ServiceOwnership.objects.bulk_create([
            ServiceOwnership(
                service=service,
                type=owner_type[1],
                owner=owner
            ) for owner in Owner.objects.filter(cmdb_id__in=to_add)
        ])

    for owner_type in owner_types:
        current_owners = set(service_from_ralph[owner_type[0]])
        previous_owners = set(service.serviceownership_set.filter(
            type=owner_type[1]
        ).values_list('owner__cmdb_id', flat=True))
        delete_obsolete_owners()
        add_new_owners()


@commit_on_success
def update_environment(env_from_ralph):
    env, created = Environment.objects.get_or_create(
        ci_id=env_from_ralph['id'],
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
        services_from_ralph = get_from_ralph("environments", logger)  # XXX filter by active
    else:
        services_from_ralph = get_from_ralph("environments", logger)
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
        for environment_id in service.get('environments', []):
            environment = Environment.objects.get(ci_id=environment_id)
            _, created = ServiceEnvironment.objects.get_or_create(
                service=service,
                environment=environment,
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

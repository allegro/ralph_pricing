# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from pyhermes.decorators import subscriber

from ralph_scrooge.models import (
    Environment,
    Service,
    ServiceEnvironment,
    OwnershipType,
    ScroogeUser,
    ServiceOwnership
)

logger = logging.getLogger(__name__)


@subscriber(topic='createService')
@subscriber(topic='updateService')
def service_environment(event_data):
    logger.info(
        'Start service environment processing for service with name: '
        '"{}" and uid: {}'.format(
            event_data.get('name'), event_data.get('uid')
        )
    )
    logger.debug('Event data: {}'.format(event_data))
    errors = _validate_service_data(event_data)
    if errors:
        msg = (
            'Error(s) detected in event data: {}. Ignoring received '
            'createService (service name: "{}", uid: {}).'
        )
        logger.error(msg.format(
            '; '.join(errors),
            event_data.get('name'),
            event_data.get('uid')
        ))
        return

    environments = _add_new_environments(event_data.get('environments', []))
    service = _update_service(event_data)
    _update_environments(service, environments)
    _update_owners(service, event_data)
    logger.info(
        'Finished service environment processing for service with name: '
        '"{}" and uid: {}'.format(event_data['name'], event_data['uid'])
    )


def _validate_service_data(event_data):
    errors = []

    if not event_data.get('uid'):
        errors.append('missing uid')
    if not event_data.get('name'):
        errors.append('missing name')
    return errors


def _add_new_environments(envs):
    environments = []
    created_environments = []
    for env_name in envs:
        obj, created = Environment.objects.get_or_create(name=env_name)
        environments.append(obj)
        if created:
            created_environments.append(obj)
    if created_environments:
        logger.info('Added new environments: {}'.format(
            [env.name for env in created_environments]
        ))
    return environments


def _update_service(event_data):
    service, created = Service.objects.update_or_create(
        ci_uid=event_data['uid'],
        defaults={
            'name': event_data['name'],
            'symbol': event_data['uid']
        }
    )
    if created:
        logger.info('Created new service with name: "{} and uid: {}'.format(
            event_data['name'], event_data['uid']
        ))
    else:
        logger.info('Updated service with name: "{}" and uid: {}'.format(
            event_data['name'], event_data['uid']
        ))

    return service


def _update_environments(service, environments):
    added_envs = []
    for env_obj in environments:
        _, created = ServiceEnvironment.objects.get_or_create(
            service=service,
            environment=env_obj,
        )
        if created:
            added_envs.append(env_obj.name)

    if added_envs:
        logger.info(
            'Added environments: {} to service name: "{}" and uid: {}'.format(
                added_envs, service.name, service.ci_uid
            )
        )


def _update_owners(service, event_data):
    owner_types = (
        ('technicalOwners', OwnershipType.technical),
        ('businessOwners', OwnershipType.business),
    )
    for owner_type in owner_types:
        current = set([
            owner['username'] for owner in event_data.get(owner_type[0], [])
        ])
        previous = set(service.serviceownership_set.filter(
            type=owner_type[1]
        ).values_list('owner__username', flat=True))

        # Delete obsolete owners.
        to_delete = previous - current
        service.serviceownership_set.filter(
            owner__username__in=to_delete,
            type=owner_type[1]
        ).delete()
        if to_delete:
            logger.info(
                'Removed {}: {} for service name: "{}" and uid: {}'.format(
                    owner_type[0], to_delete, event_data['name'],
                    event_data['uid']
                )
            )

        # Add new owners.
        to_add = current - previous
        ownerships = []
        for owner in ScroogeUser.objects.filter(username__in=to_add):
            so = ServiceOwnership(
                service=service,
                type=owner_type[1],
                owner=owner
            )
            ownerships.append(so)
        ServiceOwnership.objects.bulk_create(ownerships)
        if to_add:
            logger.info(
                'Added {}: {} for service name: "{}" and uid: {}'.format(
                    owner_type[0], to_add, event_data['name'],
                    event_data['uid']
                )
            )

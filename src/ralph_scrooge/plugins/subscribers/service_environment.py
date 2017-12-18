# -*- coding: utf-8 -*-
import logging

from pyhermes.decorators import subscriber

from ralph_scrooge.models import (
    ProfitCenter,
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
        u'Start service environment processing for service with name: '
        u'"{}" and uid: {}'.format(event_data.get('name'), event_data.get('uid'))
    )
    logger.debug(u'Event data: {}'.format(event_data))
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
        u'Finished service environment processing for service with name: '
        u'"{}" and uid: {}'.format(event_data['name'], event_data['uid'])
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
        logger.info(u'Added new environments: {}'.format(
            [env.name for env in created_environments]
        ))
    return environments


def _update_service(event_data):
    default_profit_center = ProfitCenter.objects.get(pk=1)  # from fixtures

    service, created = Service.objects.get_or_create(ci_uid=event_data['uid'])
    service.name = event_data['name']
    service.symbol = event_data['uid']
    # TODO(mbleschke) - need to set profit center but we have only name in
    # hermes event.
    service.profit_center = default_profit_center
    service.save()
    if created:
        logger.info(u'Created new service with name: "{} and uid: {}'.format(
            event_data['name'], event_data['uid']
        ))
    else:
        logger.info(u'Updated service with name: "{}" and uid: {}'.format(
            event_data['name'], event_data['uid']
        ))

    return service


def _update_environments(service, environments):
    current = set([env_obj.name for env_obj in environments])
    previous = set(service.environments.all().values_list(
        'name', flat=True)
    )

    # Delete obsolete environments.
    to_delete = previous - current
    service.environments.filter(name__in=to_delete).delete()
    if to_delete:
        logger.info(
            u'Removed environments: {} from service name: "{}" and uid: {}'.format(
                to_delete, service.name, service.ci_uid
            )
        )

    # Add new environments.
    to_add = current - previous
    for env_obj in environments:
        if env_obj.name in to_add:
            ServiceEnvironment.objects.get_or_create(
                service=service,
                environment=env_obj,
            )
    if to_add:
        logger.info(
            u'Added environments: {} to service name: "{}" and uid: {}'.format(
                to_add, service.name, service.ci_uid
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
                u'Removed {}: {} for service name: "{}" and uid: {}'.format(
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
                u'Added {}: {} for service name: "{}" and uid: {}'.format(
                    owner_type[0], to_add, event_data['name'], event_data['uid']
                )
            )

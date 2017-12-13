# -*- coding: utf-8 -*-
import logging

from pyhermes.decorators import subscriber

from ralph_scrooge.models import ProfitCenter, Environment, Service, \
    ServiceEnvironment, OwnershipType, ScroogeUser, ServiceOwnership

logger = logging.getLogger(__name__)


# TODO: also for serviceUpdate
@subscriber(topic='createService')
def service_environment(event_data):
    logger.debug('Got event data')
    logger.debug(event_data)
    errors = validate_service_data(event_data)
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

    default_profit_center = ProfitCenter.objects.get(pk=1)  # from fixtures

    # Add new environments.
    environments = []
    for env_name in event_data.get('environments', []):
        # TODO: do we need to log if created?
        obj, created = Environment.objects.get_or_create(name=env_name)
        environments.append(obj)

    # Create service.
    # TODO: create or update method
    service, created = Service.objects.get_or_create(ci_uid=event_data['uid'])
    service.name = event_data['name']
    service.symbol = event_data['uid']
    # TODO: how can we get profit center from hermes event. We have only name.
    service.profit_center = default_profit_center
    service.save()

    # Update owners
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

        # Delete obsolete owners
        to_delete = previous - current
        service.serviceownership_set.filter(
            owner__username__in=to_delete
        ).delete()

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

    # Connect service with environments.
    for env_obj in environments:
        ServiceEnvironment.objects.get_or_create(
            service=service,
            environment=env_obj,
        )


def validate_service_data(event_data):
    errors = []

    if not event_data.get('uid'):
        errors.append('missing uid')
    if not event_data.get('name'):
        errors.append('missing name')
    return errors

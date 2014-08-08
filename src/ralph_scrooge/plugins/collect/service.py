# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph.util.api_pricing import get_services
from ralph_scrooge.models import (
    BusinessLine,
    Owner,
    OwnershipType,
    Service,
    ServiceOwnership,
)


logger = logging.getLogger(__name__)


@commit_on_success
def update_service(data, date):
    service, created = Service.objects.get_or_create(
        ci_uid=data['ci_uid']
    )
    service.name = data['name']
    if data['business_line'] is not None:
        service.business_line = BusinessLine.objects.get(
            ci_uid=data['business_line']
        )
    else:
        service.business_line = None
    service.save()

    # save owners
    for owner_type in (
        ('technical_owners', OwnershipType.technical),
        ('business_owners', OwnershipType.business),
    ):
        current_owners = set(data[owner_type[0]])
        previous_owners = set(service.serviceownership_set.filter(
            type=owner_type[1]
        ).values_list(
            'owner__cmdb_id',
            flat=True
        ))

        # delete obsolete owners
        to_delete = previous_owners - current_owners
        service.serviceownership_set.filter(
            owner__cmdb_id__in=to_delete
        ).delete()

        # add new owners
        to_add = current_owners - previous_owners
        ServiceOwnership.objects.bulk_create([
            ServiceOwnership(
                service=service,
                type=owner_type[1],
                owner=owner
            ) for owner in Owner.objects.filter(cmdb_id__in=to_add)
        ])

    # save environments
    # TODO
    return created


@plugin.register(chain='scrooge', requires=['business_line', 'owner'])
def service(today, **kwargs):
    """
    Updates Services from CMDB
    """
    new_services = total = 0
    for data in get_services():
        if update_service(data, today):
            new_services += 1
        total += 1
    return True, '{} new service(s), {} updated, {} total'.format(
        new_services,
        total - new_services,
        total,
    )

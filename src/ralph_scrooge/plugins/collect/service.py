# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.transaction import commit_on_success

from ralph.util import plugin
from ralph.util.api_scrooge import get_services
from ralph_scrooge.models import (
    Environment,
    ProfitCenter,
    Owner,
    OwnershipType,
    Service,
    ServiceEnvironment,
    ServiceOwnership,
)


logger = logging.getLogger(__name__)


@commit_on_success
def update_service(data, date, default_profit_center):
    created = False
    try:
        service = Service.objects.get(
            ci_id=data['ci_id'],
        )
    except Service.DoesNotExist:
        service = Service(
            ci_id=data['ci_id'],
        )
        created = True
    service.ci_uid = data['ci_uid']
    service.name = data['name']
    service.symbol = data['symbol']
    if data['profit_center'] is not None:
        service.profit_center = ProfitCenter.objects.get(
            ci_id=data['profit_center']
        )
    else:
        service.profit_center = default_profit_center
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

    for environment_id in (data.get('environments') or []):
        environment = Environment.objects.get(ci_id=environment_id)
        ServiceEnvironment.objects.get_or_create(
            service=service,
            environment=environment,
        )
    return created


@plugin.register(chain='scrooge', requires=['profit_center', 'owner'])
def service(today, **kwargs):
    """
    Updates Services from CMDB
    """
    new_services = total = 0
    default_profit_center = ProfitCenter.objects.get(pk=1)
    for data in get_services():
        if update_service(data, today, default_profit_center):
            new_services += 1
        total += 1
    return True, '{} new service(s), {} updated, {} total'.format(
        new_services,
        total - new_services,
        total,
    )

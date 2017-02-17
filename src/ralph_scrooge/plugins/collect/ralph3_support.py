# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph_scrooge.models import PricingObject, SupportCost
from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


def _get_object_id_from_url(url):
    """
    Extract object ID from Ralph API url.
    """
    return url.rstrip('/').rpartition('/')[2]


def update_support(support):
    """
    For each base object assigned to support, create (or update or delete)
    `SupportCost` with info about support start and end and price (price is
    divided equally between all objects attached to the support).
    """
    logger.info('Processing support {}'.format(support['__str__']))
    price = float(support['price'])
    objects_ids = map(_get_object_id_from_url, support['base_objects'])
    support_cost_ids = set()
    if len(objects_ids) > 0:
        # divide cost equally for each object
        price_per_object = price / len(objects_ids)
        for obj_id in objects_ids:
            try:
                pricing_object = PricingObject.objects.get(
                    assetinfo__ralph3_asset_id=obj_id
                )
            except PricingObject.DoesNotExist:
                logger.error(
                    'PricingObject with it {} not found for support {}'.format(
                        obj_id, support['__str__']
                    )
                )
            else:
                support_cost, created = SupportCost.objects.update_or_create(
                    support_id=support['id'],
                    pricing_object=pricing_object,
                    defaults=dict(
                        start=support['date_from'],
                        end=support['date_to'],
                        cost=price_per_object,
                        forecast_cost=price_per_object,
                        remarks=support['__str__'],
                    )
                )
                support_cost_ids.add(support_cost.pk)
    # delete SupportCost for objects which no longer exists
    supports_costs_to_delete = SupportCost.objects.filter(
        support_id=support['id']
    ).exclude(
        pk__in=support_cost_ids
    )
    if supports_costs_to_delete.exists():
        logger.warning('Deleting {} support costs for {}'.format(
            supports_costs_to_delete.count(), support['__str__']
        ))
        supports_costs_to_delete.delete()
    return len(support_cost_ids)


# support costs requires assets plugin to get hypervisors
@plugin_runner.register(chain='scrooge', requires=['ralph3_asset'])
def ralph3_support(**kwargs):
    """Updates the support costs from Ralph."""

    date = kwargs['today']
    total = pricing_objects_count = 0
    for support in get_from_ralph(
        'supports', logger,
        query='date_from__lte={today}&date_to__gte={today}&price__gt=0'.format(
            today=date
        )
    ):
        total += 1
        try:
            pricing_objects_count += update_support(support)
        except:
            logger.exception(
                'Exception during processing support: {}'.format(
                    support['__str__']
                )
            )

    return True, 'Support: {} total for {} pricing objects'.format(
        total, pricing_objects_count,
    )

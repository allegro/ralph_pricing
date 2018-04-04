# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from decimal import Decimal

from ralph_scrooge.models import PricingObject
from ralph_scrooge.models.extra_cost import LicenceCost
from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect.utils import get_from_ralph

logger = logging.getLogger(__name__)


# TODO (mbleschke): common with supports
def _get_object_id_from_url(url):
    """
    Extract object ID from Ralph API url.
    """
    return url.rstrip('/').rpartition('/')[2]


def update_licence(licence):
    logger.info('Processing licence: {}'.format(licence['__str__']))

    base_objects = licence['base_objects']
    price = Decimal(licence['price'])
    licence_cost_ids = set()
    objects_ids = [
        _get_object_id_from_url(bo['base_object']) for bo in base_objects
    ]

    # TODO (mbleschke): delete LicenceCost for objects that no longer exist.
    #   Look out for dummy PricingObject
    if objects_ids:
        # TODO (mbleschke): divide price for use case when there are more
        #   purchased items than assets connected to licence.
        price_per_object = price / len(objects_ids)
        for object_id in objects_ids:
            try:
                pricing_object = PricingObject.objects.get(
                    # TODO (mbleschke): change to bo_asset_id
                    #   (waiting for other PR)
                    assetinfo__ralph3_asset_id=object_id
                )
            except PricingObject.DoesNotExist:
                logger.warning(
                    'PricingObject with it {} not found for licence {}'.format(
                        object_id, licence['__str__']
                    )
                )
            else:
                licence_cost, created = LicenceCost.objects.update_or_create(
                    licence_id=licence['id'],
                    pricing_object=pricing_object,
                    defaults=dict(
                        start=licence['invoice_date'],
                        end=licence['valid_thru'],
                        cost=price_per_object,
                        forecast_cost=price_per_object,
                        remarks=licence['__str__'],
                    )
                )
                licence_cost_ids.add(licence_cost.id)
    else:
        # TODO (mbleschke): add costs to licence service-env
        logger.info('No base objects in licence')
    return len(licence_cost_ids)


# TODO (mbleschke): add required plugins
@plugin_runner.register(chain='scrooge')
def ralph3_licence(**kwargs):
    """Updates licences from Ralph."""
    total = pricing_objects_count = 0
    # TODO: add invoice_date to query
    licences = get_from_ralph(
        'licences',
        logger,
        query='invoice_date__lte={today}&valid_thru__gte={today}&price__gte=0'.format(  # noqa: E501
            today=kwargs['today']
        )
    )
    # TODO (mbleschke): handle perpetual licences (depreciation rate)
    # perpetual_licences = get_from_ralph(
    #     'licences',
    #     logger,
    #     query='invoice_date__lte={today}&valid_thru__isnull=true&price__gte=0'.format(  # noqa: E501
    #         today=kwargs['today']
    #     )
    # )
    for licence in licences:
        total += 1
        try:
            pricing_objects_count += update_licence(licence)
        except:
            logger.exception(
                'Exception during processing licence: {}'.format(
                    licence['__str__']
                )
            )
    return True, 'Licence: {} total for {} pricing objects'.format(
        total, pricing_objects_count,
    )

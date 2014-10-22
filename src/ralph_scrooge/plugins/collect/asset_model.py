# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from ralph.util import plugin
from ralph_assets.api_scrooge import get_models
from ralph_scrooge.models import (
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
)


logger = logging.getLogger(__name__)


def update_asset_model(data):
    """
    Update information about asset model

    :param dict data: dict with information about single asset model
    :returns boolean: True, if asset model was created
    :rtype boolean:
    """
    model, created = PricingObjectModel.objects.get_or_create(
        model_id=data['model_id'],
        type_id=PRICING_OBJECT_TYPES.ASSET,
    )
    model.name = data['name']
    model.manufacturer = data['manufacturer']
    model.category = data['category']
    model.save()
    return created


@plugin.register(chain='scrooge')
def asset_model(**kwargs):
    """
    Get all information about assets models

    :returns tuple: result status, message
    """
    new = total = 0
    for model in get_models():
        total += 1
        if update_asset_model(model):
            new += 1

    return True, 'Asset models: {0} new, {1} updated, {2} total'.format(
        new,
        total-new,
        total,
    )

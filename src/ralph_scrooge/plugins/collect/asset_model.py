# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

# TODO(xor-xor): To be eventually replaced by some other plugin mechanism,
# which won't be tied to Ralph.
from ralph.util import plugin
from ralph_scrooge.models import (
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
)
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


def update_asset_model(model):
    pom, created = PricingObjectModel.objects.get_or_create(
        model_id=model['id'],
        type_id=PRICING_OBJECT_TYPES.ASSET,
    )
    pom.name = model['name']
    pom.manufacturer = model['manufacturer']['name']
    pom.category = model['category']['name']
    pom.save()
    return created


@plugin.register(chain='scrooge')
def asset_model(**kwargs):
    new = total = 0
    for model in get_from_ralph("assetmodels", logger):
        created = update_asset_model(model)
        if created:
            new += 1
        total += 1
    return True, '{} new asset models, {} updated, {} total'.format(
        new,
        total - new,
        total,
    )

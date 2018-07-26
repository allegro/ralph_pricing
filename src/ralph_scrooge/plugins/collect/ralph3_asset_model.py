# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from itertools import chain

from django.conf import settings

from ralph_scrooge.models import (
    PricingObjectModel,
    PRICING_OBJECT_TYPES,
)
from ralph_scrooge.plugins import plugin_runner
from ralph_scrooge.plugins.collect.utils import get_from_ralph


logger = logging.getLogger(__name__)


def update_asset_model(model):
    pom, created = PricingObjectModel.objects.get_or_create(
        ralph3_model_id=model['id'],
        type_id=PRICING_OBJECT_TYPES.ASSET,
    )
    pom.name = model['name']
    pom.manufacturer = (
        model['manufacturer']['name'] if model['manufacturer'] else None
    )
    pom.category = model['category']['name'] if model['category'] else None
    pom.save()
    return created


@plugin_runner.register(chain='scrooge')
def ralph3_asset_model(**kwargs):
    new = total = 0
    # fetch only data center models
    for model in chain(
        get_from_ralph("assetmodels", logger, query="type={}".format(
            settings.ASSET_MODEL_TYPE_RALPH_ID
        )),
        get_from_ralph("assetmodels", logger, query="type=4")  # type==all
    ):
        created = update_asset_model(model)
        if created:
            new += 1
        total += 1
    return True, '{} new asset models, {} updated, {} total'.format(
        new,
        total - new,
        total,
    )

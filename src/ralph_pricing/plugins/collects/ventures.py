# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph.util import plugin, api_pricing
from ralph_pricing.models import Venture


def update_venture(data):
    venture, created = Venture.objects.get_or_create(
        venture_id=data['id'],
    )
    venture.name = data['name']
    venture.department = data['department']
    venture.symbol = data['symbol']
    venture.business_segment = data['business_segment']
    venture.profit_center = data['profit_center']
    venture.is_active = data['show_in_ralph']
    if data.get('parent_id'):
        parent, parent_created = Venture.objects.get_or_create(
            venture_id=data['parent_id'],
        )
        venture.parent = parent
    else:
        venture.parent = None
        parent_created = False
    venture.save()
    return created + parent_created


@plugin.register(chain='pricing', requires=[])
def ventures(**kwargs):
    """Updates the ventures from Ralph."""

    count = sum(update_venture(data) for data in api_pricing.get_ventures())
    Venture.tree.rebuild()
    return True, '%d new ventures' % count, kwargs

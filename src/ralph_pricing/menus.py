# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_pricing.models import Venture

from bob.menu import MenuItem


def ventures_menu(ventures=None):
    if ventures is None:
        ventures = Venture.objects.filter(parent=None)
    items = []
    for venture in ventures.order_by('name'):
        item = MenuItem(
            venture.name,
            fugue_icon='fugue-store-medium',
            indent = ' ',
            collapsed = True,
            collapsible = True,
        )
        item.subitems = ventures_menu(venture.children)
        items.append(item)
    return items


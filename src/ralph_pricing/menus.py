# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_pricing.models import Venture

from bob.menu import MenuItem


def ventures_menu(href=''):
    top_items = []
    stack = [
        (top_items, Venture.objects.filter(parent=None)),
    ]
    while stack:
        items, ventures = stack.pop()
        for venture in ventures.order_by('name'):
            item = MenuItem(
                venture.name,
                name=venture.id,
                fugue_icon='fugue-store-medium',
                indent = ' ',
                href='{}/{}/'.format(href, venture.id),
                collapsed = True,
                collapsible = True,
            )
            items.append(item)
            item.subitems = []
            stack.append((item.subitems, venture.get_children()))
    return top_items


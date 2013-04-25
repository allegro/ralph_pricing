# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ralph_pricing.models import Venture

from bob.menu import MenuItem


def ventures_menu(href='', selected=None):
    top_items = []
    stack = [
        (None, top_items, Venture.objects.root_nodes()),
    ]
    while stack:
        parent, items, ventures = stack.pop()
        for venture in ventures.order_by('name'):
            item = MenuItem(
                venture.name,
                name='{}'.format(venture.id),
                subitems=[],
                fugue_icon='fugue-store-medium',
                indent = ' ',
                href='{}/{}/'.format(href, venture.id),
                collapsed = True,
                collapsible = True,
            )
            item.parent = parent
            items.append(item)
            stack.append((item, item.subitems, venture.get_children()))
            if item.name == selected:
                while item:
                    item.kwargs['collapsed'] = False
                    item = item.parent
    return top_items


# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.menu import MenuItem
from django.db.models import Q

from ralph_pricing.models import Team, Venture, UsageType


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
                indent=' ',
                href='{}/{}/'.format(href, venture.id),
                collapsed=True,
                collapsible=True,
            )
            item.parent = parent
            items.append(item)
            stack.append((item, item.subitems, venture.get_children()))
            if item.name == selected:
                while item:
                    item.kwargs['collapsed'] = False
                    item = item.parent
    return top_items


def usages_menu(href='', selected=None):
    """
    Create menus for usage types for manually entering prices
    """
    usage_types = UsageType.objects.filter(
        Q(is_manually_type=True) | Q(type='BU'),
    ).order_by('name')
    items = [
        MenuItem(
            usage_type.name,
            name=usage_type.name,
            subitems=[],
            fugue_icon='fugue-beaker',
            href='{}/{}/'.format(href, usage_type.name),
        ) for usage_type in usage_types
    ]
    return items


def teams_menu(href, selected=None):
    """
    Create menus for teams percent definitions.
    """
    teams = Team.objects.filter(billing_type='TIME').order_by('name')
    items = []
    for team in teams:
        item = MenuItem(
            team.name,
            name=team.name,
            subitems=[],
            fugue_icon='fugue-user-worker',
            href='{}/{}'.format(href, team.name),
            indent=' ',
            collapsed=True,
            collapsible=True,
        )
        if item.name == selected:
            item.kwargs['collapsed'] = False
        for dates in team.dateranges.values('start', 'end', 'id'):
            daterange = '{0} - {1}'.format(dates['start'], dates['end'])
            subitem = MenuItem(
                daterange,
                name=dates['id'],
                subitems=[],
                fugue_icon='fugue-clock',
                href='{}/{}/{}'.format(href, team.name, dates['id']),
                indent=' '
            )
            subitem.parent = item
            item.subitems.append(subitem)
        items.append(item)
    return items

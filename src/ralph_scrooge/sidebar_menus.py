# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.menu import MenuItem

from ralph_scrooge.models import (
    Team,
    TeamBillingType,
    ServiceEnvironment,
    UsageType,
    Statement,
    ExtraCostType,
)


# def ventures_menu(href='', selected=None):
#     """
#     Generate ventures submenu

#     :param string href: base url for submenu items
#     :param string selected: name of selected row
#     :returns list: list of menu items
#     :rtype list:
#     """
#     top_items = []
#     stack = [
#         (None, top_items, Venture.objects.root_nodes()),
#     ]
#     while stack:
#         parent, items, ventures = stack.pop()
#         for venture in ventures.order_by('name'):
#             item = MenuItem(
#                 venture.name,
#                 name='{}'.format(venture.id),
#                 subitems=[],
#                 fugue_icon='fugue-store-medium',
#                 indent=' ',
#                 href='{}/{}/'.format(href, venture.id),
#                 collapsed=True,
#                 collapsible=True,
#             )
#             item.parent = parent
#             items.append(item)
#             stack.append((item, item.subitems, venture.get_children()))
#             if item.name == selected:
#                 while item:
#                     item.kwargs['collapsed'] = False
#                     item = item.parent
#     return top_items


def extra_costs_menu(href='', selected=None):
    extra_costs_type = ExtraCostType.objects.all().order_by('name')
    return [
        MenuItem(
            extra_cost_type.name,
            name=extra_cost_type.name,
            subitems=[],
            fugue_icon='fugue-money-coin',
            href='{}/{}/'.format(href, extra_cost_type.id),
        ) for extra_cost_type in extra_costs_type
    ]


def service_environments(href='', service=None, environment=None):
    service_environments = ServiceEnvironment.objects.all().select_related(
        'service',
        'environment',
    ).order_by(
        'service__name',
    )
    items = {}
    for service_environment in service_environments:
        if service_environment.service.id in items:
            item = items[service_environment.service.id]
        else:
            item = MenuItem(
                service_environment.service.name,
                name=service_environment.service,
                subitems=[],
                fugue_icon='fugue-user-worker',
                href='{}/{}'.format(href, service_environment.service.id),
                indent=' ',
                collapsed=True,
                collapsible=True,
            )
            items[service_environment.service.id] = item

        if service_environment.service == service:
            item.kwargs['collapsed'] = False

        subitem = MenuItem(
            service_environment.environment.name,
            name="{0}_{1}".format(
                service_environment.service,
                service_environment.environment
            ),
            subitems=[],
            fugue_icon='fugue-clock',
            href='{}/{}/{}'.format(
                href,
                service_environment.service.id,
                service_environment.environment.id
            ),
            indent=' ',
        )
        subitem.parent = item
        item.subitems.append(subitem)
    return [v for k, v in items.iteritems()]


def statement_menu(href='', selected=None):
    """
    Generate statements submenu

    :param string href: base url for submenu items
    :param string selected: name of selected row
    :returns list: list of menu items
    :rtype list:
    """
    statements = Statement.objects.all().order_by(
        'forecast',
        '-is_active',
        'start',
    )
    items = [
        MenuItem(
            str(statement),
            name=str(statement),
            subitems=[],
            fugue_icon='fugue-clock-history',
            href='{}/{}/'.format(href, statement.id),
        ) for statement in statements
    ]
    return items


def usages_menu(href='', selected=None):
    """
    Generate usages submenu

    :param string href: base url for submenu items
    :param string selected: name of selected row
    :returns list: list of menu items
    :rtype list:
    """
    usage_types = UsageType.objects.filter(
        is_manually_type=True,
    ).order_by('name')
    items = [
        MenuItem(
            usage_type.name,
            name=usage_type.name,
            subitems=[],
            fugue_icon='fugue-beaker',
            href='{}/{}/'.format(href, usage_type.id),
        ) for usage_type in usage_types
    ]
    return items


def teams_menu(href, selected=None):
    """
    Generate teams percent definitions submenu

    :param string href: base url for submenu items
    :param string selected: name of selected row
    :returns list: list of menu items
    :rtype list:
    """
    teams = Team.objects.filter(billing_type=TeamBillingType.time).order_by(
        'name'
    )
    items = []
    for team in teams:
        item = MenuItem(
            team.name,
            name=team.name,
            subitems=[],
            fugue_icon='fugue-user-worker',
            href='{}/{}'.format(href, team.id),
            indent=' ',
            collapsed=True,
            collapsible=True,
        )
        if item.name == selected:
            item.kwargs['collapsed'] = False
        for dates in team.teamcost_set.values('start', 'end', 'id'):
            daterange = '{0} - {1}'.format(dates['start'], dates['end'])
            subitem = MenuItem(
                daterange,
                name=dates['id'],
                subitems=[],
                fugue_icon='fugue-clock',
                href='{}/{}/{}'.format(href, team.id, dates['id']),
                indent=' '
            )
            subitem.parent = item
            item.subitems.append(subitem)
        items.append(item)
    return items

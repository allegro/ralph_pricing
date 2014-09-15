# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from bob.menu import MenuItem

# from ralph.account.models import Perm
from ralph.menu import Menu


class ScroogeMenu(Menu):
    module = MenuItem(
        'Scrooge',
        name='ralph_scrooge',
        fugue_icon='fugue-money-coin',
        href='/scrooge/',
    )

    def get_submodules(self):
        return [
            # MenuItem(
            #     _("Costs report"),
            #     name='services-costs-report',
            #     fugue_icon='fugue-store-medium',
            #     view_name='services_costs_report',
            # ),
            # MenuItem(
            #     _("Service details report"),
            #     name='devices',
            #     fugue_icon='fugue-wooden-box',
            #     # view_name='devices',
            # ),
            # MenuItem(
            #     _("Usages report"),
            #     name='services-usages-report',
            #     fugue_icon='fugue-calendar-day',
            #     view_name='services_usages_report',
            # ),
            # MenuItem(
            #     _("Collect plugins"),
            #     name='services-usages-report',
            #     fugue_icon='fugue-calendar-day',
            #     view_name='services_usages_report',
            # ),
            MenuItem(
                _("Inventory"),
                name='inventory',
                fugue_icon='fugue-monitor',
                view_name='inventory',
            ),
            MenuItem(
                _("Card costs"),
                name='card_costs',
                fugue_icon='fugue-piggy-bank',
                view_name='card_costs',
            ),
            MenuItem(
                _("Dependency tree"),
                name='dependency_tree',
                fugue_icon='fugue-node',
                view_name='dependency_tree',
            ),
            MenuItem(
                _("Allocation"),
                name='allocation',
                fugue_icon='fugue-pencil',
                view_name='allocation',
            ),
            # MenuItem(
            #     _("Devices ventures changes"),
            #     name='ventures-changes',
            #     fugue_icon='fugue-arrow-switch',
            #     view_name='ventures_changes',
            # ),
            # MenuItem(
            #     _("Extra costs"),
            #     name='extra-costs',
            #     fugue_icon='fugue-money-coin',
            #     view_name='extra_costs',
            # ),
            # MenuItem(
            #     _("Usage types"),
            #     name='usage-types',
            #     fugue_icon='fugue-beaker',
            #     view_name='usage_types',
            # ),
            # MenuItem(
            #     _("Teams"),
            #     name='teams',
            #     fugue_icon='fugue-users',
            #     view_name='teams',
            # ),
            # MenuItem(
            #     _("Statements"),
            #     name='statement',
            #     fugue_icon='fugue-clock-history',
            #     view_name='statement',
            # ),
        ]

    def get_sidebar_items(self):
        return {}

menu_class = ScroogeMenu

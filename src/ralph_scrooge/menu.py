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
            MenuItem(
                _("Components"),
                name='components',
                fugue_icon='fugue-arrow-switch',
                view_name='components',
                href="/scrooge/#/components/"
            ),
            MenuItem(
                _("Cost card"),
                name='costcard',
                fugue_icon='fugue-arrow-switch',
                view_name='costcard',
                href="/scrooge/#/costcard/"
            ),
            MenuItem(
                _("Allocations admin"),
                name='components',
                fugue_icon='fugue-arrow-switch',
                view_name='components',
                href="/scrooge/#/allocation/admin/"
            ),
            ####################################################
            # [DO NOT REMOVE!] THIS PART IS FOR NEXT FEATURES
            ####################################################
            # MenuItem(
            #     _("Allocations"),
            #     name='components',
            #     fugue_icon='fugue-arrow-switch',
            #     view_name='components',
            #     href="/scrooge/#/allocation/client/"
            # ),
            ####################################################
            MenuItem(
                _("Costs report"),
                name='services-costs-report',
                fugue_icon='fugue-store-medium',
                view_name='services_costs_report',
            ),
            # MenuItem(
            #     _("Service details report"),
            #     name='devices',
            #     fugue_icon='fugue-wooden-box',
            #     # view_name='devices',
            # ),
            MenuItem(
                _("Usages report"),
                name='services-usages-report',
                fugue_icon='fugue-calendar-day',
                view_name='services_usages_report',
            ),
            MenuItem(
                _("Collect plugins"),
                name='collect-plugins',
                fugue_icon='fugue-calendar-day',
                view_name='collect_plugins',
            ),
            MenuItem(
                _("Services changes report"),
                name='services-changes-report',
                fugue_icon='fugue-arrow-switch',
                view_name='services_changes_report',
            ),
            MenuItem(
                _("Extra costs"),
                name='extra-costs',
                fugue_icon='fugue-money-coin',
                view_name='extra_costs',
            ),
            MenuItem(
                _("Usage types"),
                name='usage-types',
                fugue_icon='fugue-beaker',
                view_name='usage_types',
            ),
            MenuItem(
                _("Monthly costs"),
                name='monthly-costs',
                fugue_icon='fugue-money-bag',
                view_name='monthly_costs',
            ),
        ]

    def get_sidebar_items(self):
        return {}

menu_class = ScroogeMenu
